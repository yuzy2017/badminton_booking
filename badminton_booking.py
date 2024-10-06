from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time

# Function to calculate the next next Monday
def get_next_next_monday():
    today = datetime.now()

    # 检查今天是否是工作日（周一到周五）
    if today.weekday() < 5:  # 周一到周五对应 weekday() 为 0 到 4
        # 如果是工作日，返回下下周一（14天后）
        days_ahead = 14 - today.weekday()  # 到下周一的天数
    else:
        # 如果是周末，返回下下下周一（21天后）
        days_ahead = 21 - today.weekday()  # 到下下下周一的天数

    next_next_monday = today + timedelta(days=days_ahead)
    return int(time.mktime(next_next_monday.timetuple()))  # 转换为 Unix 时间戳

def wait_until_8_55():

    now = datetime.now()
    # 定义周一的上午8:55
    today = datetime.now()
    # 如果今天是周一且还没有到9点，返回今天的9点
    if today.weekday() == 0 and today.hour < 9:
       monday_9_00=today.replace(hour=9, minute=0, second=0, microsecond=0)
    else:
        days_ahead = (7-today.weekday())%7
        monday=today+timedelta(days=days_ahead)
        monday_9_00 = monday.replace(hour=9, minute=0, second=0, microsecond=0)
    monday_8_55 = monday_9_00.replace(hour=8, minute=55, second=0, microsecond=0)

    if now < monday_9_00:
        # 如果当前时间早于8:55，等待到8:55
        wait_time = max((monday_8_55 - now).total_seconds(),0)
        print(f"现在是 {now.strftime('%H:%M:%S')}，还没到9点，等待到8:55开始刷新...")
    else:
        # 如果当前时间已经超过9点，等待到下周一的08：55
        wait_time = (monday_8_55 - now).total_seconds()
        print(f"现在是 {now.strftime('%H:%M:%S')}，已过9点，等待到第二天8:55开始刷新...")

    # 休眠直到指定的时间
    time.sleep(wait_time)

def check_available_time_slots(driver):
    # 获取所有时间槽，包括已禁用的和可用的
    time_slots = driver.find_elements(By.XPATH, '//input[@name="timeslots[]"]')

    # 判断页面是否有可用时间槽
    if not time_slots:
        print("该日期没有可用的时间段（可能时间段未开放）。")
        return False  # 没有可用时间段

    available_slot_found = False
    for slot in time_slots:
        # 获取时间槽的 label（时间段显示的名称）
        slot_label = driver.find_element(By.XPATH, f'//label[@for="{slot.get_attribute("id")}"]').text

        # 检查是否为禁用的时间槽
        if slot.get_attribute('disabled'):
            print(f"时间段 {slot_label} 已被预订或不可用。")
        else:
            print(f"时间段 {slot_label} 可用！")
            available_slot_found = True

            # 点击可用时间槽
            driver.execute_script("arguments[0].click();", slot)
            print(f"选择了时间段：{slot_label}")

            # 点击“Add to Cart”按钮
            add_to_cart_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'add_to_chart'))  # 根据实际按钮ID替换
            )
            add_to_cart_button.click()
            print(f"已将时间段 {slot_label} 添加到购物车。")

            # 跳转到购物车页面
            driver.get("https://reboks.nus.edu.sg/nus_public_web/public/index.php/cart")
            break  # 一旦选中一个时间段，可以停止遍历
    return available_slot_found  # 返回是否找到可用时间段

# 刷新页面直到找到可用的时间槽
def refresh_until_available(driver, url, refresh_interval=30):
    available = False
    while not available:
        driver.get(url)  # 重新访问页面或刷新页面
        print("正在刷新页面...")

        available = check_available_time_slots(driver)  # 检查时间槽是否可用

        if not available:
            print(f"没有可用的时间槽，等待 {refresh_interval} 秒后重新检查...")
            time.sleep(refresh_interval)  # 等待30秒后再次刷新页面

def check_login(driver):
    current_url = driver.current_url
    while("index.php/auth" in current_url):
        print("检测到登录页面，开始执行登录操作...")

        driver.get('https://reboks.nus.edu.sg/nus_public_web/public/index.php/auth/requestAdfs')
        current_url = driver.current_url
        if not ("index.php/home" in current_url):
          # Wait for the ADFS login page to load
          WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'userNameInput')))

          # Enter NUSNET credentials
          username = driver.find_element(By.ID, 'userNameInput')
          password = driver.find_element(By.ID, 'passwordInput')

          username.send_keys('USERNAME')  # Replace with your actual ID
          password.send_keys('USERPASSWORD')  # Replace with your actual password
          password.send_keys(Keys.RETURN)
          current_url = driver.current_url
        # 提交登录表单
    print("登录成功")

def book_court(preferred_time):
    # Step 1: Setup WebDriver (assuming using Chrome)
    service = Service(executable_path='CHROMEDRIVER PATH')  # Replace with your actual path to ChromeDriver
    driver = webdriver.Chrome(service=service)

    try:
        # Step 2: Open NUS REBOKS site (use the provided URL)
        # then you need to log in first and then use this program # update for auto log in later.
        driver.get('https://reboks.nus.edu.sg/nus_public_web/public/index.php/auth/requestAdfs')

        # Wait for the ADFS login page to load
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'userNameInput')))
        # Enter NUSNET credentials
        username = driver.find_element(By.ID, 'userNameInput')
        password = driver.find_element(By.ID, 'passwordInput')

        username.send_keys('USERNAME')  # Replace with your actual ID
        password.send_keys('USERPASSWORD')  # Replace with your actual password
        password.send_keys(Keys.RETURN)
        current_url = driver.current_url
        check_login(driver)

        # Step 4: Search for available courts by date and time
        venues = {
            'Kent Ridge - Multi-purpose Sports Hall 5': 15,
            'University Town - Sports Hall 1': 21
        }
        preferred_date_timestamp = get_next_next_monday()  # Automatically calculate next next Monday's timestamp

        base_url = "https://reboks.nus.edu.sg/nus_public_web/public/index.php/facilities/view/activity/58/venue/"

        for venue, venue_id in venues.items():
            # Construct the URL for each venue with the preferred date timestamp
            target_url = f"{base_url}{venue_id}?time_from={preferred_date_timestamp}"
            driver.get(target_url)
            check_login(driver)
            driver.get(target_url)

            # Wait for the page to load and check for any available slots
           # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'court-info')))
            print(f"Checking available slots at {venue} for the date: {datetime.fromtimestamp(preferred_date_timestamp).strftime('%Y-%m-%d')}")

            # Step 5: Select an available time slot (if not disabled)
            #time_slots = driver.find_elements(By.XPATH, '//input[@name="timeslots[]" and not(@disabled)]')
            time_slots = driver.find_elements(By.XPATH, '//input[@name="timeslots[]"]')
            if not time_slots:
                print("该日期没有可用的时间段（可能时间段未开放）。")
                print("根据当前时间决定刷新策略...")
                wait_until_8_55()  # 根据时间决定什么时候开始刷新
            while not time_slots:
                    driver.get(target_url)  # 重新访问页面或刷新页面
                    print("正在刷新页面...")
                    check_login(driver)
                    driver.get(target_url)  # 重新访问页面或刷新页面
                    time_slots = driver.find_elements(By.XPATH, '//input[@name="timeslots[]"]')

                    if not time_slots:
                        print(f"没有可用的时间槽，等待 10 秒后重新检查...")
                        time.sleep(10)  # 等待10秒后再次刷新页面
            time_slots = driver.find_elements(By.XPATH, '//input[@name="timeslots[]" and not(@disabled)]')
            # 遍历每个时间槽，查找匹配的时间
            for slot in time_slots:
              # 获取时间槽的 value
              slot_value = slot.get_attribute('value')

            # 从 value 中提取时间（格式：'Badminton Court 3;572;39663;16:00:00;17:00:00'）
              time_start = slot_value.split(';')[3]  # 获取开始时间（'16:00:00'）


            # 检查时间是否匹配
              if time_start[:5] == preferred_time:
                  # 点击符合条件的时间槽
                  print(f"选择的时间槽: {slot_value}")
                  driver.execute_script("arguments[0].click();", slot)
                  # 等待“Add to Cart”按钮可点击
                  add_to_cart_button = WebDriverWait(driver, 20).until(
                      EC.element_to_be_clickable((By.ID, 'paynow'))  # 假设按钮的 ID 是 'add_to_chart'
                   )

                  # 点击“Add to Cart”按钮
                  driver.execute_script("arguments[0].click();", add_to_cart_button)
                  print("已将选定的时间槽添加到购物车。")
                  # 等待弹出框出现
                  WebDriverWait(driver, 10).until(EC.alert_is_present())

                  # 切换到弹出框并点击“确认”按钮
                  alert = driver.switch_to.alert
                  alert.accept()  # 点击确认（等同于弹窗中的“OK”或“确认”按钮）

                  print("已点击确认，转到购物车。")
                  # 等待页面加载并查找“PAY NOW”按钮
                  WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'pay')))  # 根据 name 属性查找

                  # 找到并点击“PAY NOW”按钮
                  pay_now_button = driver.find_element(By.NAME, 'pay')
                  pay_now_button.click()
                  print("已点击 'PAY NOW' 按钮，开始支付流程。")
                  break  # 一旦找到并处理了匹配的时间槽，可以结束循环
              else:
                 print("没有找到匹配的时间槽。")
                 continue

    finally:
        driver.quit()

# 用户输入的时间（要求用户输入24小时制）
#preferred_time = input("Enter the preferred time in 24-hour format (e.g., 08:00 or 13:00): ")  # 修改为24小时制
preferred_time = '14:00'
# Call the function to book court
book_court(preferred_time)
