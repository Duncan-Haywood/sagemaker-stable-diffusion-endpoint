from typing import List


def get_safe_for_work_images(prediction) -> List:
    """Filters images on whether they are safe for work or not and returns only ones that are SFW. Args: prediction (StableDiffusionPipelineOutput)

    TODO: need to test which boolean only returns SFW or NSFW content.

    return type List"""
    tuple_prediction = prediction.to_tuple()
    safe_for_work_images = [
        tuple_prediction[0][i]
        for i in range(len(tuple_prediction[1]))
        if not tuple_prediction[1][i]
    ]
    return safe_for_work_images
