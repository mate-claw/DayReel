import copy, json, re
from .config import TEMPLATE_JSON_PATH
PLACEHOLDER_RE=re.compile(r"\{\{\s*([A-Za-z0-9_\-\.]+)\s*\}\}")
class TemplateLoader:
    def load(self):
        with open(TEMPLATE_JSON_PATH,"r",encoding="utf-8") as f: return json.load(f)
    def default_merge_map(self,payload):
        out={}
        for item in payload.get("merge",[]) or []:
            if isinstance(item,dict) and "find" in item and "replace" in item: out[str(item["find"])] = item["replace"]
        return out
    def placeholders(self,payload): return sorted(set(PLACEHOLDER_RE.findall(json.dumps(payload,ensure_ascii=False))))
    def resolve(self,payload,merge):
        mp={str(i["find"]):i["replace"] for i in merge}; resolved=self._replace_recursive(copy.deepcopy(payload),mp)
        if isinstance(resolved,dict): resolved.pop("merge",None)
        return resolved
    def _replace_recursive(self,value,mp):
        if isinstance(value,dict): return {k:self._replace_recursive(v,mp) for k,v in value.items()}
        if isinstance(value,list): return [self._replace_recursive(v,mp) for v in value]
        if isinstance(value,str): return self._replace_string(value,mp)
        return value
    def _replace_string(self,value,mp):
        full=PLACEHOLDER_RE.fullmatch(value.strip())
        if full and full.group(1) in mp: return mp[full.group(1)]
        return PLACEHOLDER_RE.sub(lambda m: str(mp.get(m.group(1),m.group(0))), value)
