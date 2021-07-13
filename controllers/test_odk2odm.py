import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import glob
import os


fn = "/home/hcwinsemius/tmp/photos/DJI_0021.JPG"
folder = "/home/hcwinsemius/tmp/photos"
fns = glob.glob(os.path.join(folder, "*.JPG"))

url = "http://localhost:5001/api/odm/1/projects/6/tasks/"

# token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJlbWFpbCI6IiIsInVzZXJuYW1lIjoiaGN3aW5zZW1pdXMiLCJleHAiOjE2MjU1MDk0ODN9.m2N2PHEx2YFrtRDK9F93GgrOs2-l7tH1h4Eddz21XQ4"
# headers = {'Authorization': 'JWT {}'.format(token)}
# data = {"partial": True}

# # create a new task
# res = requests.post(
#     url,
#     headers=headers,
#     data=data,
# )
#
# task_id = res.json()["id"]
task_id = "e81186e0-d0dc-4ada-b0d9-879eb5054aa9"
print(f"New task has id: {task_id}")
url_upload = url + task_id + "/upload/"
url_update = url + task_id + "/update/"
url_commit = url + task_id + "/commit/"

#
# g = gen(fn)
# for n, data in enumerate(g):
#     print("")
#     # print(data)
# print("stop")

# images = [('images', (os.path.split(img)[-1], c, 'image/jpg'))]

# fields = {}
headers = {}
for fn in fns:
    with open(fn, "rb") as f:
        c = f.read()
        fields = {"images": (os.path.split(fn)[-1], c, 'image/jpg')}
    m = MultipartEncoder(
        fields=fields
        )
    headers["Content-type"] = m.content_type
    r = requests.post(
        url_upload,
        data=m,
        headers=headers,
    )
    print(r.json())

print(r.json())


# now commit the task for processing
r = requests.post(
    url_commit,
    headers={},
)
print(r.json())
