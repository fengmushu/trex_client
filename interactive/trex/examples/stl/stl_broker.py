
import json
import os
import zlib


class StlBrokerConfig(object):
    __TREX_CONF_JSON_F = "/tmp/paster/trex_conf.json"

    def __init__(self) -> None:
        self.config = {}
        self.updated = {}
        self.crc32 = zlib.crc32(json.dumps({}).encode('utf-8'))
        pass

    def sync(self) -> any:
        cfg = {}
        try:
            c = os.popen("cat "+self.__TREX_CONF_JSON_F, mode='r')
            cfg = json.load(c)
        except Exception as e:
            print(e)
            pass
        print("stl broker sync config")
        crc32 = zlib.crc32(json.dumps(cfg).encode('utf-8'))
        if crc32 != self.crc32:
            self.crc32 = crc32
            for k, v in self.config.items:
                if cfg.get(k) != None and cfg.get(k) != v:
                    self.updated[k] = v
                else:
                    self.updated[k] = None
            self.config = cfg

    def set(self, key, value):
        self.config[key] = value
        return self.config.get(key)

    def write(self):
        try:
            strconf = json.dumps(self.config).encode('utf-8')
            with open(self.__TREX_CONF_JSON_F, 'w') as confof:
                print(strconf)
                confof.write(strconf)
        except Exception as e:
            print(e)
            pass
        return True

    def get(self, key, default=None):
        return self.config.get(key, default)

    def dirty(self, key):
        return self.updated.get(key) != None
