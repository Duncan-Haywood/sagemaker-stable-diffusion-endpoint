
# diffusion-endpoint

Stunn diffusion model inference endpoint

## Infra options

- Sagemaker async endpoint. on ml.p2.xlarge: VCPUs:4; RAM:61 GiB; Cost-per-hour: $1.125; 1 8GB RAM GPU (I think); simple dev work.
- Sagemaker async endpoint with EIA: ml.m5.xlarge; VCPUs:4; RAM:16 GiB; Cost:$0.23; plus EIA; ml.eia1.xlarge: $0.728 or ml.eia2.xlarge; $0.476; 8GB GPU RAM for both; TODO look into other differences between the two; harder to do dev work; a few hours probably. $0.70 min total cost, though it could go down if we can get away with smaller options ie 4 GB GPU RAM (ml.eia2.large: $0.336 or ml.eia1.large: $0.364) or a smaller CPU instance which could drop by $0.10 more. Total minimum cost with smaller instances would be about $0.45 per hour.
- ECS or EKS infrastructure; ml.inf1.xlarge: VCPUs: 4; RAM:8 GiB; cost: $0.297. 1 GPU: 8 GB GPU RAM, I think. Lots of dev work, but fairly simple. Very low cost of infra.
