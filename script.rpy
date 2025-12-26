# game/script.rpy
init python:
    import json
    import webbrowser
    
    # 从整合文件导入
    from touchgal_integrated import init_crawler, search_games, get_download_links
    
    # 初始化爬虫
    init_success, init_msg = init_crawler(cache_dir="touchgal_integrated", enable_nsfw=True)
    
    # 全局变量
    search_keyword = ""
    search_results = []
    current_page = 0
    games_per_page = 6
    selected_game = None
    game_downloads = []
    current_download_page = 0
    downloads_per_page = 2
    message = ""
    message_type = "info"
    
    # 输入模式
    input_mode = "system"  # system, fallback
    is_android = renpy.android
    
    def show_message(msg, msg_type="info"):
        """显示消息"""
        global message, message_type
        store.message = msg
        store.message_type = msg_type
        renpy.restart_interaction()
    
    def clear_message():
        """清除消息"""
        global message
        store.message = ""
        renpy.restart_interaction()
    
    def show_search_input():
        """显示搜索输入窗口"""
        renpy.show_screen("search_input_screen")
    
    def perform_search():
        """执行搜索"""
        global search_results, current_page, selected_game, game_downloads, current_download_page
        
        # 检查搜索关键词是否为空或仅包含空白字符
        if not search_keyword or not search_keyword.strip():
            show_message("请输入搜索关键词", "error")
            return
        
        # 清空之前的游戏选择和下载数据
        selected_game = None
        game_downloads = []
        current_download_page = 0
        
        success, msg, results = search_games(search_keyword)
        if success:
            search_results = results
            current_page = 0
            show_message(msg, "success")
            renpy.hide_screen("search_input_screen")
            renpy.show_screen("search_results_screen")
        else:
            search_results = []
            show_message(msg, "error")
        renpy.restart_interaction()
    
    def get_downloads_for_game(game):
        """获取游戏下载"""
        global game_downloads, selected_game, current_download_page
        success, msg, downloads = get_download_links(game['id'])
        if success:
            selected_game = game
            game_downloads = downloads
            current_download_page = 0
            show_message(msg, "success")
            return True
        else:
            show_message(msg, "error")
            return False
    
    def open_link_in_browser(url):
        """在浏览器中打开链接"""
        try:
            webbrowser.open(url)
            show_message("链接已在浏览器中打开", "success")
        except Exception as e:
            show_message(f"打开失败: {str(e)}", "error")
    
    def copy_to_clipboard(text):
        """复制到剪贴板"""
        try:
            import pyperclip
            pyperclip.copy(text)
            show_message("已复制到剪贴板", "success")
        except:
            show_message("复制失败，请安装pyperclip库", "error")
    
    def get_search_placeholder_text():
        """获取搜索框占位符文本"""
        if search_keyword:
            return search_keyword
        else:
            return "点击搜索按钮输入游戏名称"
    
    def get_search_results_display_text():
        """获取搜索结果界面显示文本"""
        if search_keyword:
            return search_keyword
        else:
            return "无搜索词"

# 搜索输入窗口
screen search_input_screen():
    modal True
    zorder 100
    
    # 背景
    add "#1a1a2e"
    
    # 半透明遮罩
    add Solid("#00000080")
    
    # 输入框区域
    frame:
        background "#2d2d44"
        xalign 0.5
        yalign 0.4
        xsize 800  # 增大宽度
        ysize 400  # 增大高度
        padding (40, 40)  # 增大内边距
        
        vbox:
            spacing 30  # 增大间距
            xalign 0.5
            
            # 标题
            text "输入游戏名称":
                size 42  # 增大字体
                color "#ffffff"
                bold True
                xalign 0.5
            
            # 输入框
            frame:
                background "#3d3d5c"
                xfill True
                ysize 90  # 增大高度
                padding (25, 20)  # 增大内边距
                
                input:
                    id "search_input"
                    value VariableInputValue("search_keyword")
                    length 100
                    size 40  # 增大字体
                    color "#ffffff"
                    xalign 0.0
                    style_prefix "input_large"
            
            # 按钮行
            hbox:
                xalign 0.5
                spacing 40  # 增大按钮间距
                
                textbutton "搜 索":
                    text_size 40  # 增大字体
                    text_color "#ffffff"
                    background "#4ecdc4"
                    hover_background "#6ae6dd"
                    action If(
                        search_keyword.strip(),
                        true=Function(perform_search),
                        false=Function(show_message, "请输入搜索关键词", "error")
                    )
                    xsize 200  # 增大宽度
                    ysize 80  # 增大高度
                
                textbutton "取 消":
                    text_size 40  # 增大字体
                    text_color "#ffffff"
                    background "#4a4a6e"
                    hover_background "#5a5a8e"
                    action Hide("search_input_screen")
                    xsize 200  # 增大宽度
                    ysize 80  # 增大高度

# 主菜单界面
screen main_screen():
    tag menu
    modal True
    add "#1a1a2e"
    
    # 背景装饰
    frame:
        background "#25253c"
        xfill True
        yfill True
    
    vbox:
        xalign 0.5
        yalign 0.3
        spacing 40
        
        # 标题
        text "Galgame 游戏搜索工具" size 56 color "#ffffff" xalign 0.5
        
        # 搜索区域
        vbox:
            xalign 0.5
            spacing 25
            xsize 700
            
            # 当前搜索词显示
            frame:
                background "#2d2d44"
                xfill True
                ysize 70
                padding (20, 15)
                
                text get_search_placeholder_text():
                    size 32
                    color "#ffffff"
                    xalign 0.5
                    yalign 0.5
            
            # 按钮行
            hbox:
                xalign 0.5
                spacing 25
                
                textbutton "搜 索":
                    text_size 36
                    text_color "#ffffff"
                    background "#4ecdc4"
                    hover_background "#6ae6dd"
                    selected_background "#3dbcb4"
                    action Function(show_search_input)
                    xsize 180
                    ysize 70
                
                textbutton "清 空":
                    text_size 36
                    text_color "#ffffff"
                    background "#4a4a6e"
                    hover_background "#5a5a8e"
                    action [
                        SetVariable("search_keyword", ""),
                        Function(show_message, "搜索词已清空", "info")
                    ]
                    xsize 180
                    ysize 70
        
        # 说明文本
        text "请先在设置关闭安全输入法":
            size 28
            color "#a0a0c0"
            xalign 0.5
    
    # 底部菜单
    vbox:
        xalign 0.5
        yalign 0.9
        spacing 15
        
        textbutton "关 于":
            text_size 40
            text_color "#ffffff"
            background "#4a7c7e"
            hover_background "#5a8c8e"
            action Show("about_screen", transition=dissolve)
            xalign 0.5
            xsize 250
            ysize 75
        
        textbutton "退 出":
            text_size 40
            text_color "#ffffff"
            background "#ff6b6b"
            hover_background "#ff8585"
            action Quit()
            xalign 0.5
            xsize 250
            ysize 75
    
    # 状态信息
    if message:
        frame:
            background "#2d2d44"
            xalign 0.5
            yalign 0.95
            padding (25, 15)
            
            if message_type == "error":
                text "[message]" color "#ff6b6b" size 28
            elif message_type == "success":
                text "[message]" color "#4ecdc4" size 28
            else:
                text "[message]" color "#ffffff" size 28
    
    # 作者信息
    text "作者：Hello七七":
        size 24
        color "#a0a0c0"
        xalign 0.05
        yalign 0.98

# 搜索结果界面
screen search_results_screen():
    tag menu
    modal True
    add "#1a1a2e"
    
    # 背景装饰
    frame:
        background "#25253c"
        xfill True
        yfill True
    
    # 顶部导航栏
    frame:
        background "#2d2d44"
        xfill True
        ysize 120
        padding (20, 15)
        
        hbox:
            spacing 30
            
            # 返回按钮
            textbutton "← 返回":
                text_size 32
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action [
                    SetVariable("selected_game", None),
                    SetVariable("game_downloads", []),
                    Return()
                ]
                xsize 150
                ysize 60
            
            # 搜索框
            frame:
                background "#3d3d54"
                xfill True
                ysize 60
                padding (20, 10)
                
                input:
                    value VariableInputValue("search_keyword")
                    length 100
                    size 28
                    color "#ffffff"
                    xalign 0.0
            
            # 重新搜索按钮
            textbutton "重新搜索":
                text_size 32
                text_color "#ffffff"
                background "#4ecdc4"
                hover_background "#6ae6dd"
                action Function(show_search_input)
                xsize 200
                ysize 60
            
            # 返回主界面按钮
            textbutton "返回主界面":
                text_size 32
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action [
                    SetVariable("selected_game", None),
                    SetVariable("game_downloads", []),
                    SetVariable("search_results", []),
                    Return()
                ]
                xsize 200
                ysize 60
    
    # 标题
    text "搜索结果":
        xalign 0.5
        ypos 140
        size 48
        color "#ffffff"
        bold True
    
    # 搜索结果数量
    text "找到 {} 个游戏".format(len(search_results)):
        xalign 0.5
        ypos 190
        size 32
        color "#a0a0c0"
    
    # 搜索结果列表
    vpgrid:
        cols 2
        rows 3
        xalign 0.5
        ypos 240
        xspacing 20
        yspacing 20
        mousewheel True
        draggable True
        
        python:
            start_idx = current_page * games_per_page
            end_idx = min(start_idx + games_per_page, len(search_results))
        
        for i in range(start_idx, end_idx):
            $ game = search_results[i]
            frame:
                background "#2d2d44"
                padding (20, 20)
                xsize 600
                ysize 220
                
                vbox:
                    spacing 10
                    
                    # 游戏名称
                    text "[game['name']]":
                        size 30
                        color "#ffffff"
                        xsize 560
                        bold True
                    
                    # 游戏信息
                    vbox:
                        spacing 5
                        if game.get('platform'):
                            text "平台: {}".format(', '.join(game['platform'])):
                                size 24
                                color "#b0b0b0"
                        if game.get('language'):
                            text "语言: {}".format(', '.join(game['language'])):
                                size 24
                                color "#b0b0b0"
                    
                    # 按钮区域
                    hbox:
                        spacing 15
                        yalign 1.0
                        
                        textbutton "详 情":
                            text_size 26
                            text_color "#ffffff"
                            background "#4a4a6e"
                            hover_background "#5a5a8e"
                            action [
                                SetVariable("selected_game", game),
                                SetVariable("game_downloads", []),
                                Show("game_detail_screen")
                            ]
                            xsize 120
                            ysize 50
                        
                        textbutton "下 载":
                            text_size 26
                            text_color "#ffffff"
                            background "#4ecdc4"
                            hover_background "#6ae6dd"
                            action [
                                SetVariable("selected_game", game),
                                SetVariable("game_downloads", []),
                                Show("downloads_screen")
                            ]
                            xsize 120
                            ysize 50
    
    # 分页控制
    frame:
        background "#2d2d44"
        xalign 0.5
        ypos 740
        padding (20, 15)
        
        hbox:
            xalign 0.5
            spacing 30
            
            textbutton "上 一 页":
                text_size 28
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action If(current_page > 0, SetVariable("current_page", current_page - 1), NullAction())
                sensitive current_page > 0
                xsize 180
                ysize 60
            
            text "第 [current_page + 1] / [max(1, (len(search_results) + games_per_page - 1) // games_per_page)] 页":
                size 32
                color "#ffffff"
                yalign 0.5
            
            textbutton "下 一 页":
                text_size 28
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action If(
                    current_page < max(0, (len(search_results) - 1) // games_per_page),
                    SetVariable("current_page", current_page + 1),
                    NullAction()
                )
                sensitive current_page < max(0, (len(search_results) - 1) // games_per_page)
                xsize 180
                ysize 60

# 游戏详情界面
screen game_detail_screen():
    tag menu
    modal True
    add "#1a1a2e"
    
    # 背景装饰
    frame:
        background "#25253c"
        xfill True
        yfill True
    
    # 返回按钮
    frame:
        background "#2d2d44"
        xfill True
        ysize 100
        padding (20, 15)
        
        hbox:
            spacing 20
            
            textbutton "← 返回列表":
                text_size 32
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action [
                    SetVariable("selected_game", None),
                    SetVariable("game_downloads", []),
                    Return()
                ]
                xsize 200
                ysize 70
            
            textbutton "← 返回主界面":
                text_size 32
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action [
                    SetVariable("selected_game", None),
                    SetVariable("game_downloads", []),
                    SetVariable("search_results", []),
                    Return(True)  # 返回两层，直接回到主界面
                ]
                xsize 200
                ysize 70
    
    # 内容区域
    viewport:
        xalign 0.5
        ypos 120
        ysize 580
        scrollbars "vertical"
        mousewheel True
        draggable True
        
        vbox:
            spacing 25
            xsize 900
            
            # 游戏名称
            text "[selected_game['name']]":
                size 48
                color "#ffffff"
                bold True
                xalign 0.5
            
            # 游戏信息卡片
            frame:
                background "#2d2d44"
                padding (30, 25)
                xfill True
                
                vbox:
                    spacing 15
                    
                    if selected_game.get('alias'):
                        vbox:
                            spacing 5
                            text "别 名:":
                                size 30
                                color "#4ecdc4"
                                bold True
                            text "[selected_game['alias']]":
                                size 28
                                color "#ffffff"
                    
                    if selected_game.get('platform'):
                        vbox:
                            spacing 5
                            text "平 台:":
                                size 30
                                color "#4ecdc4"
                                bold True
                            text "{}".format(', '.join(selected_game['platform'])):
                                size 28
                                color "#ffffff"
                    
                    if selected_game.get('language'):
                        vbox:
                            spacing 5
                            text "语 言:":
                                size 30
                                color "#4ecdc4"
                                bold True
                            text "{}".format(', '.join(selected_game['language'])):
                                size 28
                                color "#ffffff"
                    
                    if selected_game.get('introduction'):
                        vbox:
                            spacing 5
                            text "简 介:":
                                size 30
                                color "#4ecdc4"
                                bold True
                            text "[selected_game['introduction']]":
                                size 26
                                color "#e0e0e0"
    
    # 底部按钮
    frame:
        background "#2d2d44"
        xfill True
        ypos 700
        padding (20, 15)
        
        hbox:
            xalign 0.5
            spacing 40
            
            textbutton "查 看 下 载":
                text_size 32
                text_color "#ffffff"
                background "#4ecdc4"
                hover_background "#6ae6dd"
                action [
                    SetVariable("game_downloads", []),
                    Show("downloads_screen")
                ]
                xsize 250
                ysize 70
            
            textbutton "返 回 列 表":
                text_size 32
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action [
                    SetVariable("selected_game", None),
                    SetVariable("game_downloads", []),
                    Return()
                ]
                xsize 250
                ysize 70

# 下载资源界面
screen downloads_screen():
    tag menu
    modal True
    add "#1a1a2e"
    
    # 背景装饰
    frame:
        background "#25253c"
        xfill True
        yfill True
    
    # 返回按钮
    frame:
        background "#2d2d44"
        xfill True
        ysize 100
        padding (20, 15)
        
        hbox:
            spacing 20
            
            textbutton "← 返回详情":
                text_size 32
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action Return()
                xsize 200
                ysize 70
            
            textbutton "← 返回主界面":
                text_size 32
                text_color "#ffffff"
                background "#4a4a6e"
                hover_background "#5a5a8e"
                action [
                    SetVariable("selected_game", None),
                    SetVariable("game_downloads", []),
                    SetVariable("search_results", []),
                    Return(True)  # 返回两层，直接回到主界面
                ]
                xsize 200
                ysize 70
    
    # 标题
    text "下载资源":
        xalign 0.5
        ypos 120
        size 48
        color "#ffffff"
        bold True
    
    text "[selected_game['name']]":
        xalign 0.5
        ypos 170
        size 32
        color "#a0a0c0"
    
    # 下载资源列表
    viewport:
        xalign 0.5
        ypos 220
        ysize 500
        scrollbars "vertical"
        mousewheel True
        draggable True
        
        vbox:
            spacing 20
            xsize 900
            
            python:
                # 如果选中的游戏不为空且下载数据为空，则获取下载数据
                if selected_game and not game_downloads:
                    success, msg, downloads = get_download_links(selected_game['id'])
                    if success:
                        game_downloads = downloads
                        show_message(msg, "success")
                    else:
                        show_message(msg, "error")
                
                start_idx = current_download_page * downloads_per_page
                end_idx = min(start_idx + downloads_per_page, len(game_downloads))
                
                # 预先计算状态文本
                if selected_game and game_downloads:
                    display_mode = "show_resources"
                elif selected_game:
                    if not game_downloads:
                        status_text = "正在获取下载资源..."
                    else:
                        status_text = "获取下载资源失败"
                    display_mode = "show_status"
                else:
                    status_text = "未选择游戏，请返回选择游戏"
                    display_mode = "show_status"
            
            if display_mode == "show_resources":
                for i in range(start_idx, end_idx):
                    $ resource = game_downloads[i]
                    frame:
                        background "#2d2d44"
                        padding (25, 20)
                        xsize 900
                        
                        vbox:
                            spacing 15
                            
                            # 资源名称
                            $ resource_num = i + 1
                            $ resource_title = str(resource['name'])
                            text "资源 [resource_num]: [resource_title]":
                                size 32
                                color "#ffffff"
                                bold True
                                xsize 850
                            
                            # 资源信息
                            vbox:
                                spacing 8
                                
                                if resource.get('platform'):
                                    hbox:
                                        spacing 10
                                        text "平台:":
                                            size 26
                                            color "#4ecdc4"
                                            bold True
                                        text "{}".format(', '.join(resource['platform'])):
                                            size 26
                                            color "#ffffff"
                                
                                if resource.get('language'):
                                    hbox:
                                        spacing 10
                                        text "语言:":
                                            size 26
                                            color "#4ecdc4"
                                            bold True
                                        text "{}".format(', '.join(resource['language'])):
                                            size 26
                                            color "#ffffff"
                                
                                if resource.get('size'):
                                    hbox:
                                        spacing 10
                                        text "大小:":
                                            size 26
                                            color "#4ecdc4"
                                            bold True
                                        text "{}".format(resource['size']):
                                            size 26
                                            color "#ffffff"
                            
                            # 链接和密码区域
                            vbox:
                                spacing 15
                                xsize 850
                                
                                if resource.get('content'):
                                    vbox:
                                        spacing 5
                                        text "下载链接:":
                                            size 28
                                            color "#4ecdc4"
                                            bold True
                                        
                                        frame:
                                            background "#3d3d54"
                                            padding (15, 12)
                                            xfill True
                                            
                                            text "[resource['content']]":
                                                size 24
                                                color "#ffffff"
                                                xsize 820
                                        
                                        hbox:
                                            spacing 20
                                            xalign 0.5
                                            
                                            textbutton "打 开 链 接":
                                                text_size 26
                                                text_color "#ffffff"
                                                background "#4ecdc4"
                                                hover_background "#6ae6dd"
                                                action Function(open_link_in_browser, resource['content'])
                                                xsize 180
                                                ysize 55
                                            
                                            textbutton "复 制 链 接":
                                                text_size 26
                                                text_color "#ffffff"
                                                background "#4a4a6e"
                                                hover_background "#5a5a8e"
                                                action Function(copy_to_clipboard, resource['content'])
                                                xsize 180
                                                ysize 55
                                
                                if resource.get('code'):
                                    vbox:
                                        spacing 5
                                        text "提取码:":
                                            size 28
                                            color "#4ecdc4"
                                            bold True
                                        
                                        hbox:
                                            spacing 15
                                            
                                            frame:
                                                background "#3d3d54"
                                                padding (15, 12)
                                                xsize 300
                                                
                                                text "[resource['code']]":
                                                    size 32
                                                    color "#ffffff"
                                                    bold True
                                                    xalign 0.5
                                            
                                            textbutton "复 制":
                                                text_size 26
                                                text_color "#ffffff"
                                                background "#4a4a6e"
                                                hover_background "#5a5a8e"
                                                action Function(copy_to_clipboard, resource['code'])
                                                xsize 120
                                                ysize 55
                                
                                if resource.get('password'):
                                    vbox:
                                        spacing 5
                                        text "解压码:":
                                            size 28
                                            color "#4ecdc4"
                                            bold True
                                        
                                        hbox:
                                            spacing 15
                                            
                                            frame:
                                                background "#3d3d54"
                                                padding (15, 12)
                                                xsize 300
                                                
                                                text "[resource['password']]":
                                                    size 32
                                                    color "#ffffff"
                                                    bold True
                                                    xalign 0.5
                                            
                                            textbutton "复 制":
                                                text_size 26
                                                text_color "#ffffff"
                                                background "#4a4a6e"
                                                hover_background "#5a5a8e"
                                                action Function(copy_to_clipboard, resource['password'])
                                                xsize 120
                                                ysize 55
            elif display_mode == "show_status":
                # 状态显示
                frame:
                    background "#2d2d44"
                    xsize 900
                    ysize 200
                    padding (25, 20)
                    xalign 0.5
                    
                    vbox:
                        xalign 0.5
                        yalign 0.5
                        spacing 20
                        
                        text "[status_text]":
                            size 36
                            color "#ffffff"
                            xalign 0.5
    
    # 分页控制
    if selected_game and game_downloads:
        frame:
            background "#2d2d44"
            xalign 0.5
            ypos 730
            padding (20, 15)
            
            hbox:
                xalign 0.5
                spacing 30
                
                textbutton "上 一 页":
                    text_size 28
                    text_color "#ffffff"
                    background "#4a4a6e"
                    hover_background "#5a5a8e"
                    action If(
                        current_download_page > 0,
                        SetVariable("current_download_page", current_download_page - 1),
                        NullAction()
                    )
                    sensitive current_download_page > 0
                    xsize 180
                    ysize 60
                
                text "第 [current_download_page + 1] / [max(1, (len(game_downloads) + downloads_per_page - 1) // downloads_per_page)] 页":
                    size 32
                    color "#ffffff"
                    yalign 0.5
                
                textbutton "下 一 页":
                    text_size 28
                    text_color "#ffffff"
                    background "#4a4a6e"
                    hover_background "#5a5a8e"
                    action If(
                        current_download_page < max(0, (len(game_downloads) - 1) // downloads_per_page),
                        SetVariable("current_download_page", current_download_page + 1),
                        NullAction()
                    )
                    sensitive current_download_page < max(0, (len(game_downloads) - 1) // downloads_per_page)
                    xsize 180
                    ysize 60

# 自定义样式
style input_large:
    size 32
    color "#ffffff"
    selected_color "#ffffff"
    caret "#4ecdc4"
    bold False

# 游戏主流程
label start:
    scene black
    
    # 显示初始化消息
    if not init_success:
        $ show_message(init_msg, "error")
    else:
        $ show_message("爬虫初始化成功！", "success")
    
    # 显示主屏幕，循环直到用户选择退出
    while True:
        call screen main_screen
        # 如果用户没有选择退出，继续显示主屏幕

# 关于屏幕
screen about_screen():
    modal True
    # 背景
    add "#1a1a2e"
    
    # 标题
    text "关于本游戏":
        size 48
        color "#ffffff"
        bold True
        xalign 0.5
        yalign 0.15
    
    # 内容区域
    frame:
        background "#2d2d44"
        xalign 0.5
        yalign 0.5
        xsize 800
        ysize 400
        padding (30, 30)
        
        vbox:
            spacing 20
            xalign 0.5
            
            text "作者联系方式":
                size 32
                color "#ffffff"
                bold True
                xalign 0.5
            
            text "QQ邮箱: 1475330840@qq.com":
                size 28
                color "#e0e0e0"
                xalign 0.5
            
            text "抖音号: 1018595100":
                size 28
                color "#e0e0e0"
                xalign 0.5
            
            text "交流群链接:":
                size 28
                color "#e0e0e0"
                xalign 0.5
            
            text "galgame创作交流群1":
                size 28
                color "#4ecdc4"
                xalign 0.5
            
            textbutton "https://qm.qq.com/q/oLPVeVuIAS":
                text_size 24
                text_color "#4ecdc4"
                text_hover_color "#6eddd4"
                background None
                xalign 0.5
                action OpenURL("https://qm.qq.com/q/oLPVeVuIAS")
    
    # 返回按钮
    textbutton "返 回":
        text_size 36
        text_color "#ffffff"
        background "#4a4a6e"
        hover_background "#5a5a8e"
        action Hide("about_screen", transition=dissolve)
        xalign 0.5
        yalign 0.85
        xsize 200
        ysize 60