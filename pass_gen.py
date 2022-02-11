import string
import secrets

def pass_gen(size=12):
   chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
   # 記号を含める場合
   chars += '%&$#()'

   return ''.join(secrets.choice(chars) for x in range(size))