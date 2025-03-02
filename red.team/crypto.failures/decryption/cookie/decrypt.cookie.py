import urllib.parse
import base64

cookie = "czN3fvCdCSDKcczc7XkgjljG56czkrNpDZFDW0MczM6Q9eCPwA7MczADLh6CuQrNsczJSvxsbPBBlIczN9mnFomIMoQczPrgEpU.6AIAcz.jB4RrwMsMscz0.eWBvJEhKIczMTKHBN9EnrwczweAHMemZsrYczpft6%2FRP5B22czejYNqeqbadAczXU1bGAA8wsgcz.7T109lzkmUcz1bXzNe8F2bYczGhbOhL6SctEczy9PVK0rau6cczam0kVBDEp22czFoh0ezQrQb6czhRv0IN%2FC2kwczFWuIGbc%2FNlMczXMwxqJ3wD5QczDyq6G.GcfOsczvWJPON0H%2FucczGsOf.YMhAxgczqbBM.yo6%2FcIczHumYz2d.bVUczb59LOKQbBR6cz4Nn1Ep6ae6oczeHj26Cd.Ga.czEiMudU5oP3AczKgH3jYy8PXk"

# Step 1: URL Decode
decoded_url = urllib.parse.unquote(cookie)
print("URL Decoded:", decoded_url)

# Step 2: Check if Base64
try:
    decoded_base64 = base64.b64decode(decoded_url).decode('utf-8')
    print("Base64 Decoded:", decoded_base64)
except:
    print("Not Base64 encoded.")

