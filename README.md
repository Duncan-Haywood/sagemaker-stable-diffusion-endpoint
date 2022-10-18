# Stable Disffusion inpaint endpoint

## Usage

### Installation

```pip install diffusion-predict
```

### for prediction run in your python file

```import diffsusion_predict
predictor = diffusion_predict.Predictor()
response = predictor.predict(args, kwargs) # see diffusers/StableDiffusionInpaintPipeline for args and kwargs
```


### for deployment run TODO

use poetry and aws-cdk lib
