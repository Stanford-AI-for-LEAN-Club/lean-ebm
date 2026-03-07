
Notes for Holger        

MSE ←∥∇yEθ(xi,˜ yi,k)−ϵ∥2

when calculating the gradient, make sure to turn on create_graph=True
grads = torch.autograd.grad(energy.sum(), x_sample, create_graph=True)[0]
* note that it doesn't calcualte gradient of loss w.r.t the parameters, just x_sample

corruption function would ideally be from "sample_langevin" (do this WITHOUT any gradient whatsoever)            
```
x_fake = self.sample_langevin(
num_samples=x.size(0),
steps=self.steps, 
step_size=self.alpha,
record_energy=False
)
```
use the sample_langevin from contrastive.py, but I will unify them later

ideally, the corruption function is tunable  
* langevin dynamcis
* corrupting the x with noise
* whatever you would like

return [total loss] , {} <-- dictionary is like your logs; you can leave empty