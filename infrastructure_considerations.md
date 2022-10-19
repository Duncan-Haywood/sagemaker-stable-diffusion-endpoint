
# diffusion-endpoint

Stunn diffusion model inference endpoint

## Infra options

- Sagemaker async endpoint. on ml.p2.xlarge: VCPUs:4; RAM:61 GiB; Cost-per-hour: $1.125; 1 12GB RAM GPU with 6 to 8 TFLOPS; simple dev work.
- Sagemaker async endpoint with EIA: ml.m5.xlarge; VCPUs:4; RAM:16 GiB; Cost:$0.23; plus EIA; ml.eia2.xlarge; $0.476; 8GB GPU RAM 32 TFLOPS; harder to do dev work; several hours probably; the model needs to be ported into . $0.70 minimum total cost on a smaller CPU instance (ml.r5.large or ml.m5.large approximately $0.15 or $0.11) which could drop costs by $0.12 more. Total minimum cost with smaller instance would be about $0.59 per hour.
- Inf1 ECS: Needs compiling, and seems that the instance type does not support diffusers: ECS or EKS infrastructure; ml.inf1.xlarge: VCPUs: 4; RAM:8 GiB; cost: $0.297. 1 GPU: 8 GB GPU RAM, I think.
- Similar to sagemaker with EIA, but on ECS; the same instances cost less outside of sagemaker. r6g.medium 1 VCPU, 8 GB RAM (needs to be able to run on AMD graviton chips); $0.05 plus eia2.xlarge $0.34 brings us to $0.39 hourly cost with similar performance; there would be additional overhead costs of networking, etc that would need to be considered.

## Dev notes

Predict functionality can be updated to handle further concurency and performance by switching to multi-threading and sagemaker predict_async() function. It can also be further optimized by switching to boto, but this wouldn't be necessary unless we are seeing significant traffic. At which point, it would likely be better to move to ECS or EKS as noted in infrastructure_considerations.md