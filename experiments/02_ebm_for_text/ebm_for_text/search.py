# Best-first search over structured states using proposal + energy model + tools.
from __future__ import annotations

import heapq
import logging
import time

import torch

from .data_types import Action, SearchNode, SearchResult, SearchState
from .energy_model import EnergyModel
from .proposal import ProposalModel
from .retrieval import Retriever
from .tools import ToolAdapter

log = logging.getLogger(__name__)


def best_first_search(
    problem: str,
    initial_state: SearchState,
    energy_model: EnergyModel,
    proposal: ProposalModel,
    tool: ToolAdapter,
    retriever: Retriever,
    *,
    budget: int = 100,
    beam_width: int = 10,
    lambda_value: float = 0.5,
    num_candidates: int | None = None,
    mode: str = "code",
    device: str = "cpu",
) -> SearchResult:
    """Run best-first search.

    Pseudocode from the proposal (§5):
    ```
    frontier = {s0}
    while budget remains:
        s = pop_best(frontier)
        R = retrieve_context(s)
        A = q_phi.sample_k(s, R)
        for a in A:
            s', diag = tool_execute(s, a)
            if invalid(s', diag):
                continue
            score = e_theta(s, a, R, diag) + λ * V_theta(s')
            push(frontier, s', cumulative_score + score)
        if solved(s):
            return extract_solution(s)
    ```
    """
    root = SearchNode(state=initial_state, cumulative_energy=0.0, depth=0)
    frontier: list[SearchNode] = [root]
    heapq.heapify(frontier)
    nodes_expanded = 0
    best_node = root

    t0 = time.time()

    while frontier and nodes_expanded < budget:
        node = heapq.heappop(frontier)
        nodes_expanded += 1

        if node.cumulative_energy < best_node.cumulative_energy:
            best_node = node

        # Check if solved
        if node.state.is_solved and node.depth > 0:
            log.info(
                "Solved after %d expansions (depth=%d, energy=%.4f)",
                nodes_expanded, node.depth, node.cumulative_energy,
            )
            return SearchResult(
                solved=True,
                solution=node.state.code_or_proof,
                trajectory=_extract_trajectory(node),
                nodes_expanded=nodes_expanded,
                best_energy=node.cumulative_energy,
            )

        # Retrieve context for current state
        context = retriever.retrieve(node.state)

        # Generate candidate actions from proposal model
        candidates = proposal.generate_candidates(
            node.state,
            context=context,
            mode=mode,
            num_candidates=num_candidates,
        )

        if not candidates:
            continue

        # Execute each candidate and collect valid successors
        valid_states: list[SearchState] = []
        valid_actions: list[Action] = []
        valid_contexts: list[str] = []

        for action in candidates:
            new_state, is_valid = tool.execute(node.state, action)
            if not is_valid:
                continue
            valid_states.append(new_state)
            valid_actions.append(action)
            valid_contexts.append(context)

        if not valid_states:
            continue

        # Score valid successors with energy model
        energies, values = energy_model.score(
            problem, valid_states, valid_actions, valid_contexts, device=device
        )

        # Compute combined scores and push to frontier
        for i, (s, a) in enumerate(zip(valid_states, valid_actions)):
            step_score = energies[i].item() + lambda_value * values[i].item()
            child = SearchNode(
                state=s,
                cumulative_energy=node.cumulative_energy + step_score,
                depth=node.depth + 1,
                parent=node,
                action=a,
            )
            heapq.heappush(frontier, child)

        # Keep frontier bounded
        if len(frontier) > beam_width:
            frontier = heapq.nsmallest(beam_width, frontier)
            heapq.heapify(frontier)

        if nodes_expanded % 10 == 0:
            elapsed = time.time() - t0
            log.info(
                "Expanded %d nodes (frontier=%d, best_energy=%.4f, %.1fs)",
                nodes_expanded, len(frontier), best_node.cumulative_energy, elapsed,
            )

    # Budget exhausted — return best effort
    log.info("Budget exhausted after %d expansions", nodes_expanded)
    return SearchResult(
        solved=False,
        solution=best_node.state.code_or_proof,
        trajectory=_extract_trajectory(best_node),
        nodes_expanded=nodes_expanded,
        best_energy=best_node.cumulative_energy,
    )


def _extract_trajectory(
    node: SearchNode,
) -> list[tuple[SearchState, Action]]:
    """Walk parent pointers to reconstruct the path from root to node."""
    path: list[tuple[SearchState, Action]] = []
    cur = node
    while cur.parent is not None and cur.action is not None:
        path.append((cur.state, cur.action))
        cur = cur.parent
    path.reverse()
    return path
