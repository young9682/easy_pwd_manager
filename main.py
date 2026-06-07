import easygui as eg
import pyperclip
import database
import password_gen
import strength

def init():
    database.init_db()

def generate():
    # 密码长度输入
    length_input = eg.integerbox(
        '密码长度',
        default=16,
        lowerbound=4,
        upperbound=64
    )
    if length_input is None:
        return

    # 字符类型选择
    choices = ["大写字母 (A-Z)", "小写字母 (a-z)", "数字 (0-9)", "特殊符号 (!@#$...)"]
    defaults = [True, True, True, False]

    result = eg.multchoicebox(
        '选择包含的字符类型:',
        '密码生成设置',
        choices,
        preselect=defaults
    )

    # 解析选择结果
    use_upper = any("大写字母" in c for c in result)
    use_lower = any("小写字母" in c for c in result)
    use_nums = any("数字" in c for c in result)
    use_syms = any("特殊符号" in c for c in result)

    # 生成密码
    pwd = password_gen.generate_password(length_input, use_upper, use_lower, use_nums, use_syms)
    info = strength.check_strength(pwd)

    # 显示生成的密码
    pwd_message = f"""生成的密码：{pwd}

强度：{info['level']} ({info['score']}/100)
熵值：{info['entropy']} bits"""

    eg.msgbox(pwd_message, '密码生成结果', ok_button='保存')

    # 输入服务名称和用户名
    fields = ["服务名称 (如 'Google')", "用户名 (可选)"]
    user_input = eg.multenterbox('请输入信息', '保存密码', fields)
    if user_input is None:
        return

    name = user_input[0].strip()
    username = user_input[1].strip() if len(user_input) > 1 else ""

    if not name:
        eg.msgbox("服务名称不能为空", "提示")
        return

    # 保存到数据库
    database.add_password(
        name, username, pwd, length_input,
        int(use_upper), int(use_lower),
        int(use_nums), int(use_syms),
        info['score']
    )
    eg.msgbox(f"已保存:\n\n服务：{name}\n密码：{pwd}", "保存成功")

def list_passwords():
    rows = database.get_all_passwords()
    if not rows:
        eg.msgbox("没有保存的密码记录", "密码列表")
        return

    # 格式化显示数据
    display_data = []
    for row in rows:
        pid, name, username, pwd, length, score, created = row
        level = "强" if score >= 80 else "中" if score >= 60 else "弱"
        display_data.append(f"ID:{pid} | {name} | {username or '-'} | 长度:{length} | {level}({score})")

    # 显示列表（choicebox 至少需要两个选项）
    if len(display_data) == 1:
        selected_id = str(rows[0][0])
    else:
        choice = eg.choicebox(
            "已保存的密码列表",
            "选择一条记录查看详情",
            display_data
        )

        if choice is None:
            return

        selected_id = choice.split('|')[0].replace('ID:', '').strip()

    # 显示完整密码，提供复制选项
    rows = database.get_all_passwords()
    for row in rows:
        if str(row[0]) == selected_id:
            pid, name, username, pwd, length, score, created = row
            level = "强" if score >= 80 else "中" if score >= 60 else "弱"

            pwd_info = f"""服务：{name}
用户名：{username or '-'}
密码：{pwd}
长度：{length}
强度：{level} ({score}/100)"""

            eg.msgbox(pwd_info, "密码详情")

            if eg.ccbox(msg="是否复制密码到剪贴板？", title="操作"):
                pyperclip.copy(pwd)
                eg.msgbox("密码已复制到剪贴板", "复制成功")
            break

def delete_password():
    rows = database.get_all_passwords()
    if not rows:
        eg.msgbox("没有保存的密码记录", "删除密码")
        return

    # 格式化显示数据
    display_data = []
    for row in rows:
        pid, name, username, pwd, length, score, created = row
        level = "强" if score >= 80 else "中" if score >= 60 else "弱"
        display_data.append(f"ID:{pid} | {name} | {username or '-'} | 长度:{length} | {level}({score})")

    # 显示列表（choicebox 至少需要两个选项）
    if len(display_data) == 1:
        selected_id = str(rows[0][0])
    else:
        choice = eg.choicebox(
            "已保存的密码列表",
            "选择要删除的密码",
            display_data
        )

        if choice is None:
            return

        selected_id = choice.split('|')[0].replace('ID:', '').strip()

    # 确认删除
    if eg.ccbox(msg="确定要删除此密码吗？", title="确认删除"):
        database.delete_password(selected_id)
        eg.msgbox(f"已删除 ID:{selected_id}", "删除成功")

def main():
    init()

    # 主循环
    while True:
        choice = eg.choicebox(
            msg='请选择操作',
            title='简易密码管理器',
            choices=['生成密码', '查看密码列表', '删除密码', '退出']
        )
        if choice is None:
            break
        if choice == '生成密码':
            generate()
        elif choice == '查看密码列表':
            list_passwords()
        elif choice == '删除密码':
            delete_password()
        elif choice == '退出':
            eg.msgbox("再见！", "退出程序")
            break

if __name__ == "__main__":
    main()
