"""Collect only public GitHub Trending metadata. Standard library only."""
from datetime import datetime,timezone
from pathlib import Path
import html
import json
import re
from urllib.request import Request,build_opener,HTTPRedirectHandler

PERIODS=('daily','weekly','monthly')
LIMIT=3_000_000


def text(value):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',value))).strip()


def parse(body,period):
    articles=re.findall(r'<article\b[^>]*class=["\'][^"\']*\bBox-row\b[^"\']*["\'][^>]*>([\s\S]*?)</article>',body)
    result=[];seen=set()
    for article in articles:
        heading=re.search(r'<h2\b[^>]*>([\s\S]*?)</h2>',article)
        match=re.search(r'href=["\']/([^"\']+)["\']',heading.group(1)) if heading else None
        name=html.unescape(match.group(1)) if match else ''
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',name) or len(name)>180 or any(p in ('.','..') for p in name.split('/')) or name.lower() in seen:raise ValueError('Unexpected repository identifier')
        seen.add(name.lower())
        def count(suffix):
            match=re.search(r'href=["\']/'+re.escape(name)+'/'+suffix+r'["\'][^>]*>([\s\S]*?)</a>',article,re.I)
            value=text(match.group(1)) if match else ''
            return int(value.replace(',','')) if re.fullmatch(r'[\d,]+',value) else None
        gain=re.search(r'([\d,]+)\s+stars\s+'+{'daily':'today','weekly':'this week','monthly':'this month'}[period],text(article))
        description=re.search(r'<p\b[^>]*>([\s\S]*?)</p>',article)
        result.append({'repo':name,'description':text(description.group(1))[:1200] if description else '',
            'stars':count('stargazers'),'forks':count('forks'),'rank':len(result)+1,'period_stars':int(gain.group(1).replace(',','')) if gain else None})
    if not 1<=len(result)<=100:raise ValueError('Unexpected empty or oversized Trending page')
    return result


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


def read(period):
    req=Request('https://github.com/trending?since='+period,headers={'User-Agent':'Public-Trending-Snapshot/1.0','Accept-Language':'en','Accept-Encoding':'identity'})
    with build_opener(NoRedirect).open(req,timeout=25) as response:
        data=response.read(LIMIT+1)
        if len(data)>LIMIT:raise ValueError('Response too large')
        return data.decode('utf-8')


def collect(previous,fetch=read):
    now=datetime.now(timezone.utc).isoformat();periods={};failed=[]
    for period in PERIODS:
        old=previous.get('periods',{}).get(period,{})
        row={'source_url':'https://github.com/trending?since='+period,'attempted_at':now}
        try:row.update(status='completed',fetched_at=now,items=parse(fetch(period),period))
        except Exception:
            # No exception bodies, HTML, request headers or authentication in output.
            row.update(status='failed',fetched_at=old.get('fetched_at',''),items=old.get('items',[]));failed.append(period)
        periods[period]=row
    return {'schema_version':1,'source':'github-trending','generated_at':now,'periods':periods},failed


def main():
    path=Path('data/trending.json')
    previous=json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
    snapshot,failed=collect(previous)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(path)
    print(json.dumps({'counts':{p:len(v['items']) for p,v in snapshot['periods'].items()},'failed':failed}))
    Path('collection-status.txt').write_text('failed' if failed else 'completed',encoding='utf-8')


if __name__=='__main__':main()
