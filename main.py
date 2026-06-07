import easygui as eg
import pyperclip
import database
import password_gen
import strength

def init():
    database.init_db()

def input_password():
    """手动输入密码并保存"""
    fields = ["服务名称 (如 'Google')", "用户名 (可选)", "密码"]
    user_input = eg.multenterbox('请输入以下信息', '手动输入密码', fields)
    if user_input is None:
        return

    name = user_input[0].strip()
    username = user_input[1].strip() if len(user_input) > 1 else ""
    pwd = user_input[2].strip() if len(user_input) > 2 else ""

    if not name:
        eg.msgbox("服务名称不能为空", "提示")
        return
    if not pwd:
        eg.msgbox("密码不能为空", "提示")
        return

    info = strength.check_strength(pwd)

    cred_id = database.add_credential(name, username)
    database.add_password_analysis(
        cred_id, pwd, len(pwd),
        int(any(c.isupper() for c in pwd)),
        int(any(c.islower() for c in pwd)),
        int(any(c.isdigit() for c in pwd)),
        int(any(not c.isalnum() for c in pwd)),
        info['score']
    )
    eg.msgbox(f"已保存:\n\n服务：{name}\n密码：{pwd}\n强度：{info['level']} ({info['score']}/100)", "保存成功")

def generate_password():
    """生成密码并保存"""
    length_input = eg.integerbox('密码长度(4-64)', default=16, lowerbound=4, upperbound=64)
    if length_input is None:
        return

    choices = ["大写字母 (A-Z)", "小写字母 (a-z)", "数字 (0-9)", "特殊符号 (!@#$...)"]
    defaults = [True, True, True, False]
    result = eg.multchoicebox('选择包含的字符类型:', '密码生成设置', choices, preselect=defaults)
    if result is None:
        return

    use_upper = any("大写字母" in c for c in result)
    use_lower = any("小写字母" in c for c in result)
    use_nums = any("数字" in c for c in result)
    use_syms = any("特殊符号" in c for c in result)

    pwd = password_gen.generate_password(length_input, use_upper, use_lower, use_nums, use_syms)
    info = strength.check_strength(pwd)

    pwd_message = f"""生成的密码：{pwd}

强度：{info['level']} ({info['score']}/100)
熵值：{info['entropy']} bits"""

    eg.msgbox(pwd_message, '密码生成结果', ok_button='保存')

    fields = ["服务名称 (如 'Google')", "用户名 (可选)"]
    user_input = eg.multenterbox('请输入信息', '保存密码', fields)
    if user_input is None:
        return

    name = user_input[0].strip()
    username = user_input[1].strip() if len(user_input) > 1 else ""
    if not name:
        eg.msgbox("服务名称不能为空", "提示")
        return

    cred_id = database.add_credential(name, username)
    database.add_password_analysis(cred_id, pwd, length_input,
        int(use_upper), int(use_lower), int(use_nums), int(use_syms), info['score'])
    eg.msgbox(f"已保存:\n\n服务：{name}\n密码：{pwd}", "保存成功")

def change_password():
    """选择已有凭据，用四种模式之一修改密码并重新评分"""
    rows = database.get_all_credentials()
    if not rows:
        eg.msgbox("没有保存的凭据", "修改密码")
        return

    display_data = []
    for row in rows:
        pid, name, username, pwd, length, score, _ = row
        level = "强" if score >= 80 else "中" if score >= 60 else "弱"
        display_data.append(f"ID:{pid} | {name} | {username or '-'} | {level}({score})")

    if len(display_data) == 1:
        selected_id = str(rows[0][0])
    else:
        choice = eg.choicebox("选择要修改密码的凭据", "修改密码", display_data)
        if choice is None:
            return
        selected_id = choice.split('|')[0].replace('ID:', '').strip()

    # 选择生成模式
    mode = eg.choicebox("选择新密码生成方式", "修改密码", [
        "1. 手动输入密码",
        "2. 随机生成（默认）",
        "3. 纯数字",
        "4. 纯字母",
        "5. 数字+字母"
    ])
    if mode is None:
        return

    if "手动输入" in mode:
        pwd = eg.enterbox("输入新密码", "修改密码")
        if not pwd:
            return
        length = len(pwd)
        use_upper = any(c.isupper() for c in pwd)
        use_lower = any(c.islower() for c in pwd)
        use_nums = any(c.isdigit() for c in pwd)
        use_syms = any(not c.isalnum() for c in pwd)
    elif "纯数字" in mode:
        pwd = password_gen.generate_password(length=16, use_upper=False, use_lower=False, use_nums=True, use_syms=False)
        length = 16
        use_upper = use_lower = use_syms = False
        use_nums = True
    elif "纯字母" in mode:
        pwd = password_gen.generate_password(length=16, use_upper=True, use_lower=True, use_nums=False, use_syms=False)
        length = 16
        use_nums = use_syms = False
        use_upper = use_lower = True
    elif "数字+字母" in mode:
        pwd = password_gen.generate_password(length=16, use_upper=True, use_lower=True, use_nums=True, use_syms=False)
        length = 16
        use_syms = False
        use_upper = use_lower = use_nums = True
    else:
        pwd = password_gen.generate_password(length=16, use_upper=True, use_lower=True, use_nums=True, use_syms=True)
        length = 16
        use_syms = True
        use_upper = use_lower = use_nums = True

    info = strength.check_strength(pwd)

    pwd_message = f"""新密码：{pwd}

强度：{info['level']} ({info['score']}/100)
熵值：{info['entropy']} bits"""

    eg.msgbox(pwd_message, '密码修改结果')

    if eg.ccbox(msg="确定使用此密码？", title="确认"):
        database.add_password_analysis(
            int(selected_id), pwd, length,
            int(use_upper), int(use_lower), int(use_nums), int(use_syms), info['score']
        )
        # 查找服务名称
        for r in rows:
            if str(r[0]) == selected_id:
                eg.msgbox(f"密码已更新\n\n服务：{r[1]}\n新密码：{pwd}", "修改成功")
                break

def list_passwords():
    """查看密码列表及历史"""
    rows = database.get_all_credentials()
    if not rows:
        eg.msgbox("没有保存的密码记录", "密码列表")
        return

    display_data = []
    for row in rows:
        pid, name, username, pwd, length, score, _ = row
        level = "强" if score >= 80 else "中" if score >= 60 else "弱"
        display_data.append(f"ID:{pid} | {name} | {username or '-'} | 长度:{length} | {level}({score})")

    if len(display_data) == 1:
        selected_id = str(rows[0][0])
    else:
        choice = eg.choicebox("已保存的密码列表", "选择一条记录查看详情", display_data)
        if choice is None:
            return
        selected_id = choice.split('|')[0].replace('ID:', '').strip()

    # 显示密码历史
    history = database.get_password_history(int(selected_id))
    if not history:
        eg.msgbox("无密码记录", "密码详情")
        return

    # 当前密码
    pwd, length, score, created = history[0]
    level = "强" if score >= 80 else "中" if score >= 60 else "弱"

    detail = f"当前密码：{pwd}\n强度：{level} ({score}/100)\n创建时间：{created}"
    if len(history) > 1:
        detail += f"\n\n--- 历史记录（共 {len(history)} 条）---"
        for h in history[1:]:
            p, l, s, t = h
            lv = "强" if s >= 80 else "中" if s >= 60 else "弱"
            detail += f"\n{p} | {lv}({s}) | {t}"

    eg.msgbox(detail, "密码详情")

    if eg.ccbox(msg="是否复制当前密码到剪贴板？", title="操作"):
        pyperclip.copy(pwd)
        eg.msgbox("密码已复制到剪贴板", "复制成功")

def delete_password():
    """删除凭据及其所有密码记录"""
    rows = database.get_all_credentials()
    if not rows:
        eg.msgbox("没有保存的密码记录", "删除密码")
        return

    display_data = []
    for row in rows:
        pid, name, username, pwd, length, score, _ = row
        level = "强" if score >= 80 else "中" if score >= 60 else "弱"
        display_data.append(f"ID:{pid} | {name} | {username or '-'} | {level}({score})")

    if len(display_data) == 1:
        selected_id = str(rows[0][0])
    else:
        choice = eg.choicebox("选择要删除的凭据", "删除密码", display_data)
        if choice is None:
            return
        selected_id = choice.split('|')[0].replace('ID:', '').strip()

    if eg.ccbox(msg="确定要删除此凭据及所有密码记录吗？", title="确认删除"):
        database.delete_credential(int(selected_id))
        eg.msgbox(f"已删除凭据 ID:{selected_id}", "删除成功")

def main():
    init()

    while True:
        choice = eg.choicebox(
            msg='请选择操作',
            title='简易密码管理器',
            choices=['生成密码', '输入密码', '修改密码', '查看密码列表', '删除密码', '退出']
        )
        if choice is None:
            break
        if choice == '生成密码':
            generate_password()
        elif choice == '输入密码':
            input_password()
        elif choice == '修改密码':
            change_password()
        elif choice == '查看密码列表':
            list_passwords()
        elif choice == '删除密码':
            delete_password()
        elif choice == '退出':
            eg.msgbox("再见！", "退出程序")
            break

if __name__ == "__main__":
    main()
