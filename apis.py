import base64
import sys

sys.path.append("..")

from gcp_tools.gcs import GCS
from gcp_tools.veo2 import Veo2

import os
from dynaconf import Dynaconf


def profile_file(filename: str):
    return os.path.realpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    )


settings: Dynaconf = Dynaconf(
    settings_files=[profile_file('development.yaml'), profile_file('production.yaml')],
    warn_dynaconf_global_settings=True,
    environments=True,
    lowercase_read=False,
)

project_id = settings.get("gcp.project_id")
location = settings.get("gcp.location")
bucket = settings.get("gcp.out_bucket")
service_account = settings.get("gcp.service_account")

veo2 = Veo2(
    project_id=project_id,
    location=location,
    bucket=bucket,
    service_account=service_account
)

gcs = GCS(service_account=settings.get("gcp.service_account"))


# 定义API调用函数
def call_video_generation_api(data):
    prompt_ = data.get("prompt")
    image = data.get("image")
    bucket_name = veo2.bucket.replace('gs://', '')
    if image:
        urls = veo2.generate_video_from_image(
            prompt=prompt_,
            image_bytes=base64.b64encode(data["image"]).decode("ascii"),
            image_type=data["file_type"],
            aspect_ratio=data["aspect_ratio"],
            number_of_videos=data['number_of_videos'],
            duration_seconds=data['duration_seconds'],
            person_generation=data['person_generation'])
        return [(gcs.generate_signed_url(bucket_name, url.replace(veo2.bucket + '/', '')), url.split("/")[-1]) for url
                in urls]
    else:
        urls = veo2.generate_video_from_text(prompt=prompt_,
                                             aspect_ratio=data["aspect_ratio"],
                                             number_of_videos=data['number_of_videos'],
                                             duration_seconds=data['duration_seconds'],
                                             person_generation=data['person_generation'])
        return [(gcs.generate_signed_url(bucket_name, url.replace(veo2.bucket + '/', '')), url.split("/")[-1]) for url
                in urls]
