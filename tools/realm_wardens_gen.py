#!/usr/bin/env python3
"""Realm Wardens asset generation driver for the bound TapTap Maker project.

Talks to the official TapTap Maker MCP runtime bundled with the Cindy plugin
(same TAPTAP_MAKER_HOME and credentials), so batches can run unattended.

Usage:
  python3 tools/realm_wardens_gen.py concepts [--groups hero,tower] [--limit N]
  python3 tools/realm_wardens_gen.py models   [--groups prop,enemy] [--parallel 4] [--limit N]
  python3 tools/realm_wardens_gen.py art      [--limit N]
  python3 tools/realm_wardens_gen.py status
"""
import argparse, json, os, subprocess, sys, threading, time, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "docs", "realm-wardens", "manifest.json")
STATE = os.path.join(ROOT, "docs", "realm-wardens", "state.json")
LOG = os.path.join(ROOT, "docs", "realm-wardens", "run.log")

NODE = "/Users/xd/homebrew/opt/node-official/node"
SERVER = os.path.expanduser(
    "~/Library/Application Support/Cindy/owners/c26228c97e9ad71f3007/"
    "cindy-brain/taptap-maker/vendor/taptap-maker/dist/maker.js")

_state_lock = threading.Lock()
_log_lock = threading.Lock()


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    with _log_lock:
        print(line, flush=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, STATE)


def patch_state(key, **fields):
    with _state_lock:
        st = load_state()
        cur = st.get(key, {})
        cur.update(fields)
        cur["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        st[key] = cur
        save_state(st)
    return cur


class Client:
    """One stdio MCP session against the Maker runtime."""

    def __init__(self):
        self.p = subprocess.Popen(
            [NODE, SERVER], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.id = 0
        self.resp = {}
        self.lock = threading.Lock()
        threading.Thread(target=self._read, daemon=True).start()
        self._call("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "rw-batch", "version": "1.0"}})
        self._notify("notifications/initialized")

    def _read(self):
        assert self.p.stdout is not None
        for line in self.p.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                continue
            if "id" in msg:
                with self.lock:
                    self.resp[msg["id"]] = msg

    def _notify(self, method):
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
        self.p.stdin.flush()

    def _call(self, method, params=None, timeout=1800):
        self.id += 1
        rid = self.id
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            msg["params"] = params
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self.lock:
                if rid in self.resp:
                    return self.resp.pop(rid)
            time.sleep(0.05)
        raise TimeoutError(method)

    def call(self, name, args):
        r = self._call("tools/call", {"name": name, "arguments": args})
        res = r.get("result", {})
        sc = res.get("structuredContent")
        if sc:
            return sc
        # fall back to parsing text content
        txt = "".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        if res.get("isError"):
            raise RuntimeError(txt[:600])
        try:
            return json.loads(txt)
        except Exception:
            return {"raw_text": txt}

    def close(self):
        try:
            self.p.stdin.close()
        except Exception:
            pass
        self.p.terminate()


TD = ROOT


# --------------------------------------------------------------------- concepts
def concept_prompt(asset, man):
    return asset["prompt"] + "\n" + man["style_block"]


def run_concepts(groups, limit, batch=6):
    man = json.load(open(MANIFEST, encoding="utf-8"))
    st = load_state()
    todo = [a for a in man["assets"]
            if a["concept"] and (not groups or a["group"] in groups)
            and not st.get(f"concept:{a['id']}", {}).get("path")]
    if limit:
        todo = todo[:limit]
    log(f"concepts: {len(todo)} to generate")
    c = Client()
    while todo:
        chunk, todo = todo[:batch], todo[batch:]
        items = [{"prompt": concept_prompt(a, man), "name": f"rw_{a['id']}_concept",
                  "aspect_ratio": "1:1", "target_size": "1024x1024", "resolution": "1K"}
                 for a in chunk]
        try:
            res = c.call("batch_generate_images", {"images": items, "target_dir": TD})
        except Exception as exc:
            log(f"concepts batch failed: {exc}")
            continue
        got = {}
        for entry in res.get("results", res.get("images", [])) or []:
            name = str(entry.get("name", ""))
            path = entry.get("localPath") or entry.get("absolutePath")
            for a in chunk:
                if f"rw_{a['id']}_concept" == name and path:
                    got[a["id"]] = path
        if not got:
            log(f"concepts batch unknown shape: {json.dumps(res)[:400]}")
        for a in chunk:
            if a["id"] in got:
                patch_state(f"concept:{a['id']}", path=got[a["id"]], status="done")
                log(f"concept ok {a['id']} -> {got[a['id']]}")
            else:
                log(f"concept missing {a['id']}")
    c.close()


# ----------------------------------------------------------------------- models
SUBJECT_LABEL = {"biped": "humanoid character", "quadruped": "four-legged creature",
                 "other": "object", "scenery": "scene"}


def models_pending(groups, limit, st, man):
    out = []
    for a in man["assets"]:
        if groups and a["group"] not in groups:
            continue
        rec = st.get(f"model:{a['id']}", {})
        if rec.get("status") == "done":
            continue
        out.append((a, rec))
    return out[:limit] if limit else out


def start_model(c, a, man, st):
    rec = st.get(f"model:{a['id']}", {})
    if rec.get("asset_id") and rec.get("status") in ("running", "queued"):
        return rec
    opts = {"face_limit": a["face_limit"], "texture": True, "pbr": False}
    payload = {"quality_tier": a["quality_tier"], "subject_type": a["subject_type"]}
    concept = st.get(f"concept:{a['id']}", {}).get("path")
    if a["concept"] and concept:
        payload["generation_strategy"] = "direct"
        payload["images"] = {"front": concept}
        payload["prompt"] = f"stylized hand-painted low-poly fantasy {SUBJECT_LABEL[a['subject_type']]}"
    else:
        payload["generation_strategy"] = "direct"
        payload["prompt"] = f"{a['prompt']} {man['style_block']} {man['add3d_block']}"
        opts["negative_prompt"] = man["negative_block"]
    payload["options"] = opts
    res = c.call("create_3d_asset", {"action": "start", "target_dir": TD, "payload": payload})
    aid = res.get("asset_id")
    patch_state(f"model:{a['id']}", asset_id=aid, task_id=res.get("task_id"),
                status=res.get("status", "running"), step=res.get("current_step"),
                quality=a["quality_tier"])
    log(f"start {a['id']} asset={aid} status={res.get('status')}")
    return {"asset_id": aid, "status": res.get("status")}


def worker(assets, man, wid):
    c = Client()
    try:
        for a in assets:
            key = f"model:{a['id']}"
            try:
                rec = load_state().get(key, {})
                if rec.get("status") == "done":
                    continue
                if not rec.get("asset_id"):
                    start_model(c, a, man, load_state())
                deadline = time.time() + 1800
                while time.time() < deadline:
                    rec = load_state().get(key, {})
                    aid = rec.get("asset_id")
                    if not aid:
                        break
                    r = c.call("create_3d_asset", {"action": "query", "asset_id": aid, "target_dir": TD})
                    status = r.get("status")
                    if status in ("completed", "success"):
                        ld = (r.get("local_delivery") or {}).get("model") or {}
                        patch_state(key, status="done", step=r.get("current_step"),
                                    model_path=ld.get("local_path"),
                                    remote_url=(r.get("model") or {}).get("url"))
                        log(f"done {a['id']} -> {ld.get('local_path')}")
                        break
                    if status in ("failed", "error"):
                        patch_state(key, status="failed", error=json.dumps(r)[:400])
                        log(f"FAILED {a['id']}: {json.dumps(r)[:300]}")
                        break
                    patch_state(key, status=status or "running", step=r.get("current_step"))
                    time.sleep(12)
                else:
                    log(f"timeout {a['id']}")
                    patch_state(key, status="timeout")
            except Exception as exc:
                log(f"error {a['id']}: {exc}")
                patch_state(key, status="error", error=str(exc)[:300])
    finally:
        c.close()


def run_models(groups, parallel, limit):
    man = json.load(open(MANIFEST, encoding="utf-8"))
    st = load_state()
    pending = models_pending(groups, limit, st, man)
    assets = [a for a, _ in pending]
    log(f"models: {len(assets)} pending, parallel={parallel}")
    if not assets:
        return
    buckets = [[] for _ in range(parallel)]
    for i, a in enumerate(assets):
        buckets[i % parallel].append(a)
    threads = [threading.Thread(target=worker, args=(b, man, i), daemon=True)
               for i, b in enumerate(buckets) if b]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# -------------------------------------------------------------------------- art
def run_art(limit):
    man = json.load(open(MANIFEST, encoding="utf-8"))
    st = load_state()
    todo = [im for im in man["images"] if not st.get(f"art:{im['id']}", {}).get("path")]
    if limit:
        todo = todo[:limit]
    log(f"art: {len(todo)} to generate")
    c = Client()
    for im in todo:
        prompt = im["prompt"] + "\n" + man["style_block"]
        if im["transparent"]:
            prompt += "\ntransparent background"
        try:
            res = c.call("generate_image", {
                "prompt": prompt, "name": f"rw_{im['id']}",
                "aspect_ratio": im["ratio"] if im["ratio"] != "8:3" else "3:2",
                "target_size": im["size"], "resolution": "2K" if im["size"] != "256x256" else "1K",
                "transparent": im["transparent"], "target_dir": TD})
            path = res.get("localPath")
            patch_state(f"art:{im['id']}", path=path, status="done")
            log(f"art ok {im['id']} -> {path}")
        except Exception as exc:
            log(f"art failed {im['id']}: {exc}")
    c.close()


def run_status():
    st = load_state()
    man = json.load(open(MANIFEST, encoding="utf-8"))
    counts = {}
    for kind in ("concept", "model", "art"):
        src = man["assets"] if kind != "art" else man["images"]
        done = sum(1 for a in src if st.get(f"{kind}:{a['id']}", {}).get("status") == "done"
                   or (kind == "concept" and st.get(f"concept:{a['id']}", {}).get("path")))
        counts[kind] = f"{done}/{len(src)}"
    print(json.dumps(counts, indent=1))
    for k, v in sorted(st.items()):
        if v.get("status") in ("failed", "error", "timeout"):
            print(k, v.get("status"), v.get("error", "")[:160])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["concepts", "models", "art", "status"])
    ap.add_argument("--groups", default="")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    groups = [g for g in args.groups.split(",") if g]
    if args.cmd == "concepts":
        run_concepts(groups, args.limit)
    elif args.cmd == "models":
        run_models(groups, args.parallel, args.limit)
    elif args.cmd == "art":
        run_art(args.limit)
    else:
        run_status()


if __name__ == "__main__":
    main()
