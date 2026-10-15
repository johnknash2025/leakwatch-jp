import argparse
import json
import sys

from . import mail, playbooks
from .llm import Client
from .severity import ACTION_TEXT, LABEL_JA, LEVELS, classify, recommended_actions
from .sources import REGISTRY, get_source
from .store import Store

STATUS_JA = {"open": "未対応", "done": "対応済み"}


def cmd_add(a, st):
    st.add_email(a.email); st.save(); print(f"登録しました: {a.email}")


def cmd_remove(a, st):
    st.remove_email(a.email); st.save(); print(f"削除しました: {a.email}")


def cmd_check(a, st):
    src = get_source(a.source)
    emails = [a.email] if a.email else st.data["emails"]
    if not emails:
        print("メールアドレスが未登録です: leakwatch add you@example.com"); return 1
    for e in emails:
        breaches = src.check_email(e.lower())
        print(f"\n■ {e}: {len(breaches)}件の漏洩" if breaches else f"\n■ {e}: 漏洩は見つかりませんでした")
        for b in breaches:
            sev = classify(b)
            st.upsert_finding(e.lower(), b, sev, recommended_actions(b))
            print(f"  [{LABEL_JA[sev]}] {b.title} ({b.breach_date}) 項目: {', '.join(b.data_classes)}")
    st.save()
    print("\n対応一覧: leakwatch status")


def cmd_status(a, st):
    items = sorted(st.data["findings"].items(),
                   key=lambda kv: (kv[1]["status"] == "done", -LEVELS.index(kv[1]["severity"])))
    if a.json:
        print(json.dumps(dict(items), ensure_ascii=False, indent=2)); return
    if not items:
        print("記録はありません（leakwatch check を実行してください）"); return
    for fid, f in items:
        if a.open and f["status"] == "done":
            continue
        print(f"[{STATUS_JA[f['status']]}][{LABEL_JA[f['severity']]}] {fid}")
        for act in f["actions"]:
            print(f"    - {ACTION_TEXT[act]}")
        pb = playbooks.find_for_domain(f["domain"])
        if pb:
            print(f"    手順: leakwatch guide {pb['id']}")


def cmd_done(a, st, status="done"):
    try:
        st.set_status(a.id, status)
    except KeyError:
        print(f"見つかりません: {a.id}"); return 1
    st.save(); print(f"{STATUS_JA[status]}にしました: {a.id}")


def cmd_guide(a, st):
    if not a.service:
        for s in playbooks.load():
            print(f"{s['id']:20} {s['name']}")
        return
    s = playbooks.get(a.service)
    if not s:
        print(f"見つかりません: {a.service}"); return 1
    print(f"■ {s['name']}  ※最後の操作はご本人が行ってください")
    for i, step in enumerate(s["steps"], 1):
        print(f"  {i}. {step}")
    for l in s["links"]:
        tag = "確認済み" if l.get("verified") else "未確認・公式サイトで要確認"
        print(f"  リンク: {l['label']} {l['url']} （{tag}）")
    for p in s["phones"]:
        tag = "確認済み" if p.get("verified") else "未確認"
        print(f"  電話: {p['label']} {p['number']} （{tag}）")
    if s.get("unverified_note"):
        print(f"  注意: {s['unverified_note']}")


def cmd_mail(a, st):
    text = open(a.file, encoding="utf-8", errors="replace").read() if a.file != "-" else sys.stdin.read()
    r = mail.inspect(text)
    if a.llm:
        c = Client()
        r["llm"] = mail.llm_review(text, c) if c.enabled else "LEAKWATCH_LLM_URL が未設定"
    print(json.dumps(r, ensure_ascii=False, indent=2))


def cmd_sources(a, st):
    for name, cls in REGISTRY.items():
        print(f"{name:10} {'使用可' if cls().available() else 'キー未設定'}")


def build_parser():
    p = argparse.ArgumentParser(prog="leakwatch", description="自分の情報漏洩チェック＆対応支援（ローカル）")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add", help="メールアドレスを登録"); s.add_argument("email"); s.set_defaults(f=cmd_add)
    s = sub.add_parser("remove", help="登録を削除"); s.add_argument("email"); s.set_defaults(f=cmd_remove)
    s = sub.add_parser("check", help="漏洩を確認"); s.add_argument("email", nargs="?")
    s.add_argument("--source", default="hibp", choices=list(REGISTRY)); s.set_defaults(f=cmd_check)
    s = sub.add_parser("status", help="対応状況を表示"); s.add_argument("--open", action="store_true")
    s.add_argument("--json", action="store_true"); s.set_defaults(f=cmd_status)
    s = sub.add_parser("done", help="対応済みにする"); s.add_argument("id"); s.set_defaults(f=cmd_done)
    s = sub.add_parser("reopen", help="未対応に戻す"); s.add_argument("id")
    s.set_defaults(f=lambda a, st: cmd_done(a, st, "open"))
    s = sub.add_parser("guide", help="サービス別の対応手順"); s.add_argument("service", nargs="?"); s.set_defaults(f=cmd_guide)
    s = sub.add_parser("mail", help="届いた警告メールを点検（- で標準入力）"); s.add_argument("file")
    s.add_argument("--llm", action="store_true"); s.set_defaults(f=cmd_mail)
    s = sub.add_parser("sources", help="情報源の一覧"); s.set_defaults(f=cmd_sources)
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return a.f(a, Store()) or 0
    except (RuntimeError, NotImplementedError, ValueError) as e:
        print(f"エラー: {e}", file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
