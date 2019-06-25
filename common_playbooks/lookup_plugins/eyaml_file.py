from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible import utils, errors

import yaml
import hashlib
from Crypto.Cipher import AES

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        ret = []
        if len(terms) > 0:
            encrypted_yaml_file = terms[0]
            display.vvvv("File lookup using %s as file" % encrypted_yaml_file)
            if encrypted_yaml_file:
                key = hashlib.sha256("AMLINFRA@OPS".encode('utf-8'))
                key_cipher = AES.new(key.digest(), AES.MODE_ECB)
                with open(encrypted_yaml_file, 'rb') as f:
                    try:
                        x = key_cipher.decrypt(f.read())
                        cfg_frag = yaml.safe_load(x)
                        ret.append(cfg_frag)
                    except Exception as e:
                        raise AnsibleError("Error in loading the file" % str(e))
        return ret
