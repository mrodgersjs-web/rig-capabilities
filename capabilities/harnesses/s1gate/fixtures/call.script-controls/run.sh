for f in "$@"; do
 ~/.rig/bin/rig-s1gate check call.script --file "$f" --subject "human-read call script" --json 2>/dev/null | python3 -c "
import json,sys;d=json.load(sys.stdin);a={k:v.get('noul') for k,v in d['answers'].items()}
print('$(basename $f)',d['verdict'],round(min(a.values()),2),' '.join(f'{k}={v}' for k,v in a.items()),'|',';'.join(d['reasons'])[:160])"
done
