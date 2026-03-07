# Goal: lora fine tune the best: **Selected model: Goedel-Prover-V2-32B with LoRA on 1x B200 (GPU 6, 183 GB)**

- 90.4% MiniF2F-test (SOTA among open models)
- LoRA est. ~80 GB VRAM -- leaves ~100 GB headroom for activations, batch size, etc.
- HuggingFace: https://huggingface.co/Goedel-LM/Goedel-Prover-V2-32B
- TODO: test actual VRAM usage with a trial run

great! so let's in the py_src create a training script for lora for this model and train it on the validaiton set of mini-f2f; https://huggingface.co/datasets/brando/minif2f-lean4 please. Test it and use a free gpu     
  and test it on the minif2flean4 test; the goal will be to have the val loss go down and let's see what happens to the test loss  