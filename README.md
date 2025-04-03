## 修改 `development.yaml`
```yaml
development:
  gcp:
    project_id: xxxx
    location: xxxx
    video_model: veo-2.0-generate-001
    out_bucket: gs://xxxxx
    service_account: sa账号路径（放在项目根目录下就行）
```
## 使用cloud build构建镜像
替换实践的project_id
```shell
gcloud builds submit --tag gcr.io/[project_id]/veo2-demo  .
```
## 使用cloud run启动镜像
```shell
gcloud run deploy veo2-app --image gcr.io/[project_id]/veo2-demo  --platform managed  --region us-central1  --allow-unauthenticated --port 8501 --service-account [sa账号名]
```