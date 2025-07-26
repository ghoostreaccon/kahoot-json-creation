import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Config paths
CHROMIUM_PATH = r"[PATH to the browser]"
CHROMEDRIVER_PATH = r"PATH to your chromedriver"

# Load quiz data
with open(r"kahoot_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

options = Options()
options.binary_location = CHROMIUM_PATH
options.add_argument("--headless=new")  # Remove if you want to see the browser
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-usb-discovery")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
wait = WebDriverWait(driver, 20)
driver.implicitly_wait(10)

try:
    # --- STEP 1: LOGIN ---
    driver.get("https://create.kahoot.it/login")
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys(data["username"])
    driver.find_element(By.NAME, "password").send_keys(data["password"])
    driver.find_element(By.XPATH, "//button[contains(text(),'Log in')]").click()
    time.sleep(5)

    # --- STEP 2: GO TO CREATE PAGE ---
    driver.get("https://create.kahoot.it/create")
    time.sleep(5)
    
    buttons_to_try = [
        "Close",
        "Next",
        "Skip",
        "Start from scratch",
    ]

    for btn_text in buttons_to_try:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{btn_text}')]")))
            btn.click()
            time.sleep(2)
            break
        except:
            continue

    try:
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Enter kahoot title')]")))
        btn.click()
        time.sleep(2)
    except:
        Exception


    title_input = wait.until(EC.presence_of_element_located((By.ID, "kahoot-title")))
    title_input.clear()
    title_input.send_keys(data["title"])
    time.sleep(1)

    done_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Done')]")))
    done_btn.click()
    time.sleep(3)

    # --- STEP 3: Create Questions ---
    for q in data["questions"]:
        try:
            add_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-functional-selector='add-question-button']")
            ))
            add_btn.click()
            time.sleep(2)
        except:
            print("⚠️ Could not click 'Add question' button.")
            continue

        try:   
            add_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-functional-selector='create-button__quiz']")
            ))
            add_btn.click()
            time.sleep(2)
        except:
            print("⚠️ Could not click 'Quiz' button.")
            continue

        try:
            q_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@data-functional-selector='question-title__input']")
            ))
            q_input.click()
            question_text = f"{q['question']['title']}"
            q_input.send_keys(question_text)
            time.sleep(1)
        except:
            print("⚠️ Could not enter question text.")
            continue

        try:
            answer_blocks = driver.find_elements(By.XPATH, "//div[@data-functional-selector='question-answer__input']")

            for i, ans in enumerate(q["choices"]):
                try:
                    ans_input = wait.until(EC.presence_of_element_located((By.ID, f"question-choice-{i}")))
                    ans_input.click()
                    ans_input.clear()
                    ans_input.send_keys(ans)
                    time.sleep(0.5)
                except:
                    print(f"⚠️ Could not write answer {i+1}")
        except:
            print("⚠️ Answer input fields not found.")
            continue

        try:
            toggle_buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//button[@data-functional-selector='question-answer__toggle-button']")))

            if q["correct"] < len(toggle_buttons):
                selected_toggle = toggle_buttons[q["correct"]]

                if selected_toggle.get_attribute("aria-checked") != "true":
                    driver.execute_script("arguments[0].click();", selected_toggle)
                    time.sleep(1)
                else:
                    print("✔️ Correct answer already selected.")
            else:
                print(f"⚠️ Correct index {q['correct']} out of range for toggle buttons.")
        except Exception as e:
            print(f"⚠️ Could not set correct answer: {e}")

    try:
        s_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-functional-selector='top-bar__save-button']")))
        s_input.click()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Error trying to save. {e}")


        
    print("✅ Kahoot creation complete!")

finally:
    driver.quit()
