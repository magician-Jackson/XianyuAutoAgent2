import os
import shutil
import time
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import set_key
from loguru import logger

from utils.xianyu_utils import generate_device_id, generate_sign, trans_cookies


MESSAGE_URL = os.getenv(
    "BROWSER_LOGIN_URL",
    "https://www.goofish.com/im?spm=a21ybx.home.sidebar.2.4c053da6K6mu08",
)
TOKEN_API_URL = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemessage.pc.login.token/1.0/"
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("BROWSER_LOGIN_TIMEOUT", "300"))
POLL_INTERVAL_MS = int(os.getenv("BROWSER_LOGIN_POLL_INTERVAL_MS", "2000"))
PROFILE_DIR = Path(os.getenv("BROWSER_LOGIN_PROFILE_DIR", "data/browser_profile"))
COOKIE_PLACEHOLDER = "your_cookies_here"
IMPORTANT_COOKIE_NAMES = {"unb", "_m_h5_tk", "cna", "cookie2", "XSRF-TOKEN"}
IMPORTANT_DOMAIN_SUFFIXES = (
    "goofish.com",
    "taobao.com",
    "tmall.com",
)
REQUEST_HEADERS = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "origin": "https://www.goofish.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.goofish.com/",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.0.0 Safari/537.36"
    ),
}


def _is_relevant_cookie(cookie: Dict[str, str]) -> bool:
    name = cookie.get("name", "")
    domain = cookie.get("domain", "").lstrip(".").lower()

    return name in IMPORTANT_COOKIE_NAMES or any(
        domain.endswith(suffix) for suffix in IMPORTANT_DOMAIN_SUFFIXES
    )


def _build_cookie_string(cookies: List[Dict[str, str]]) -> str:
    deduplicated = OrderedDict()

    for cookie in cookies:
        name = cookie.get("name")
        value = cookie.get("value")
        if name and value is not None:
            deduplicated[name] = value

    return "; ".join(f"{name}={value}" for name, value in deduplicated.items())


def _extract_cookie_string(cookies: List[Dict[str, str]]) -> str:
    relevant_cookies = [cookie for cookie in cookies if _is_relevant_cookie(cookie)]
    source_cookies = relevant_cookies or cookies
    return _build_cookie_string(source_cookies)


def _has_required_login_cookies(cookies: List[Dict[str, str]]) -> bool:
    names = {cookie.get("name") for cookie in cookies if cookie.get("value")}
    return {"unb", "_m_h5_tk"}.issubset(names)


def _persist_cookie_string(cookie_str: str, env_path: str) -> None:
    env_file = Path(env_path)
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.touch(exist_ok=True)
    set_key(str(env_file), "COOKIES_STR", cookie_str)


def reset_browser_login_state(env_path: str = ".env", clear_profile: bool = True) -> None:
    """清空旧 Cookie 和浏览器 profile，强制下次重新登录。"""
    env_file = Path(env_path)
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.touch(exist_ok=True)
    set_key(str(env_file), "COOKIES_STR", COOKIE_PLACEHOLDER)

    if clear_profile and PROFILE_DIR.exists():
        shutil.rmtree(PROFILE_DIR, ignore_errors=True)


def _launch_context(playwright, profile_dir: Path, preferred_channel: Optional[str]):
    channels = []
    for channel in [preferred_channel, "msedge", "chrome", None]:
        if channel not in channels:
            channels.append(channel)

    last_error = None
    for channel in channels:
        try:
            launch_kwargs = {
                "headless": False,
                "viewport": {"width": 1440, "height": 900},
                "args": ["--disable-blink-features=AutomationControlled"],
            }
            if channel:
                launch_kwargs["channel"] = channel

            context = playwright.chromium.launch_persistent_context(
                str(profile_dir),
                **launch_kwargs,
            )
            browser_name = channel or "chromium"
            return context, browser_name
        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "无法启动浏览器。请先确认本机已安装 Edge/Chrome，"
        "或执行 `playwright install chromium` 后重试。"
        f" 原始错误: {last_error}"
    )


def _validate_cookie_string(cookie_str: str) -> Dict[str, str]:
    cookies = trans_cookies(cookie_str)
    user_id = cookies.get("unb", "")
    token = cookies.get("_m_h5_tk", "").split("_")[0]

    if not user_id or not token:
        return {"ok": False, "status": "missing_cookie", "message": "缺少关键 Cookie"}

    device_id = generate_device_id(user_id)
    timestamp = str(int(time.time()) * 1000)
    data_val = (
        '{"appKey":"444e9908a51d1cb236a27862abc769c9",'
        f'"deviceId":"{device_id}"'
        "}"
    )
    params = {
        "jsv": "2.7.2",
        "appKey": "34839810",
        "t": timestamp,
        "sign": generate_sign(timestamp, token, data_val),
        "v": "1.0",
        "type": "originaljson",
        "accountSite": "xianyu",
        "dataType": "json",
        "timeout": "20000",
        "api": "mtop.taobao.idlemessage.pc.login.token",
        "sessionOption": "AutoLoginOnly",
        "spm_cnt": "a21ybx.im.0.0",
    }

    try:
        response = requests.post(
            TOKEN_API_URL,
            params=params,
            data={"data": data_val},
            cookies=cookies,
            headers=REQUEST_HEADERS,
            timeout=20,
        )
        payload = response.json()
    except requests.RequestException as exc:
        return {"ok": False, "status": "network_error", "message": str(exc)}
    except ValueError as exc:
        return {"ok": False, "status": "invalid_json", "message": str(exc)}

    ret_list = payload.get("ret", [])
    ret_text = " | ".join(ret_list) if isinstance(ret_list, list) else str(ret_list)

    if any("SUCCESS::调用成功" in ret for ret in ret_list) and payload.get("data", {}).get("accessToken"):
        return {
            "ok": True,
            "status": "success",
            "message": ret_text,
            "access_token": payload["data"]["accessToken"],
        }

    if "RGV587_ERROR" in ret_text or "被挤爆啦" in ret_text:
        return {"ok": False, "status": "risk_control", "message": ret_text}

    if "FAIL_SYS_SESSION_EXPIRED" in ret_text or "SESSION_EXPIRED" in ret_text:
        return {"ok": False, "status": "expired", "message": ret_text}

    if "FAIL_SYS_LOGIN" in ret_text or "请先登录" in ret_text:
        return {"ok": False, "status": "not_logged_in", "message": ret_text}

    return {"ok": False, "status": "token_invalid", "message": ret_text or str(payload)}


def launch_browser_login_and_get_cookie_str(
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    env_path: str = ".env",
    preferred_channel: Optional[str] = None,
) -> str:
    """打开消息页，等待用户扫码登录并完成滑块，再保存可用 Cookie。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "未安装 playwright，请先执行 `pip install -r requirements.txt`"
        ) from exc

    profile_dir = PROFILE_DIR
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context, browser_name = _launch_context(
            playwright,
            profile_dir,
            preferred_channel or os.getenv("BROWSER_LOGIN_CHANNEL"),
        )

        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(MESSAGE_URL, wait_until="domcontentloaded", timeout=60000)
            page.bring_to_front()

            logger.info(f"已打开 {browser_name} 闲鱼消息页，请扫码登录")
            logger.info("如果页面出现滑块，请在消息页完成验证后保持页面停留")
            logger.info(f"程序会持续校验 Cookie 是否真的可用，最长等待 {timeout_seconds} 秒")

            deadline = time.time() + timeout_seconds
            last_cookie_names = set()
            last_status = None
            last_message = None

            while time.time() < deadline:
                if "/im" not in page.url:
                    try:
                        page.goto(MESSAGE_URL, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        pass

                page.wait_for_timeout(POLL_INTERVAL_MS)
                cookies = context.cookies()

                if cookies:
                    last_cookie_names = {
                        cookie.get("name") for cookie in cookies if cookie.get("name")
                    }

                if not _has_required_login_cookies(cookies):
                    continue

                cookie_str = _extract_cookie_string(cookies)
                if not cookie_str:
                    continue

                validation = _validate_cookie_string(cookie_str)
                status = validation.get("status")
                message = validation.get("message")

                if validation.get("ok"):
                    _persist_cookie_string(cookie_str, env_path)
                    logger.success("已获取并验证可用 Cookie，已写入 .env")
                    return cookie_str

                if status != last_status or message != last_message:
                    if status == "risk_control":
                        logger.warning("检测到风控或滑块未完成，请在消息页完成验证，程序会自动重试")
                    elif status in {"expired", "not_logged_in", "missing_cookie"}:
                        logger.info("登录态还没完全准备好，继续等待消息页登录完成")
                    else:
                        logger.info(f"Cookie 已拿到，但暂时还不可用: {message}")

                last_status = status
                last_message = message

            known_cookies = ", ".join(sorted(last_cookie_names)) if last_cookie_names else "无"
            raise TimeoutError(
                "等待登录超时，仍未拿到可通过 token 校验的 Cookie。"
                f" 当前已检测到的 Cookie: {known_cookies}"
            )
        finally:
            context.close()


def main() -> int:
    try:
        launch_browser_login_and_get_cookie_str()
        return 0
    except Exception as exc:
        logger.error(f"浏览器登录获取 Cookie 失败: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
