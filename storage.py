import w3storage
import os
from dotenv import load_dotenv

load_dotenv()

w3s = w3storage.API(token=os.getenv('WEB3_STORAGE_KEY'))

some_uploads = w3s.user_uploads(size=25)

# limited to 100 MB
helloworld_cid = w3s.post_upload(('hello_World.txt', 'Hello, world.'))
readme_cid = w3s.post_upload(('README.md', open('README.md', 'rb')))

print(helloworld_cid)
print(readme_cid)

