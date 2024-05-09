import json
from copy import copy
from dataclasses import dataclass
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver


@dataclass
class Tools:
    browser: webdriver
    url = 'https://reseau-ges.percipio.com'
    prefix = "===== "
    def connection(self, usr: str, pwd: str) -> bool:
        print(self.prefix + "Logging in")
        # On dit au navigateur d'aller sur l'url suivant
        self.browser.get('https://reseau-ges.percipio.com/login%2F#/')

        sleep(2)

        # type text
        text_area = self.browser.find_element('id', 'loginName')
        text_area.send_keys(usr)

        # click submit button
        next_btn = self.browser.find_element("xpath", "//button[@class='Button---root---2BQqW Button---primary---1O3lq "
                                                      "Button---small---3PMLN Button---center---13Oaw']")
        next_btn.click()

        sleep(1)

        # type text
        text_area = self.browser.find_element('id', 'password')
        text_area.send_keys(pwd)

        # click submit button
        submit_button = self.browser.find_element("xpath", "//button[@class='Button---root---2BQqW "
                                                           "Button---primary---1O3lq Button---small---3PMLN "
                                                           "Button---center---13Oaw']")
        submit_button.click()

        sleep(5)
        print(self.prefix + "Logged in")

        return True

    def check_exists_by_xpath(self, xpath) -> bool:
        try:
            self.browser.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True

    def go_to_assignment(self) -> bool:
        self.browser.get('https://reseau-ges.percipio.com/assignments')
        return True

    def get_all_courses(self):
        btn_show_detail = self.browser.find_elements(By.CSS_SELECTOR,
                                                     ".Button---root---2BQqW.Button---flat---fb6Ta.Button---medium---1CC5_.Button---center---13Oaw")
        for btn in btn_show_detail:
            ActionChains(self.browser).move_to_element(btn).click().perform()
            sleep(1)

        a_courses = self.browser.find_elements(By.CSS_SELECTOR, ".Link---root---U3vzY.Link---focus---V5Bo7")
        courses = []
        for a in a_courses:
            courses.append(a.get_attribute('href'))
        return courses

    def get_cours(self, course_url: str) -> None:
        self.browser.get(course_url)

    def get_video(self, video_url: str):
        self.browser.get(video_url)

    def get_videos(self, video_id: str) -> None:
        self.browser.get(self.url + '/videos/' + video_id)

    def get_test(self, test_url: str) -> None:
        self.browser.get(test_url)

    def launch_video(self) -> str:
        # Lancement de la vidéo
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ContentItem---link---ILx7P")))

        videos = self.browser.find_elements(By.CLASS_NAME, 'ContentItem---link---ILx7P')
        status_span = self.browser.find_elements(By.CSS_SELECTOR, ".ContentItem---status---w1Me0")[::2]
        titles = self.browser.find_elements(By.CSS_SELECTOR, ".ContentItem---title---kdZSE")
        video_titles = []
        for title in titles:
            title_text = title.find_element(By.XPATH,
                                            "./child::*").find_elements(By.XPATH, "./child::*")[0].text
            video_titles.append(title_text)
        print(self.prefix +"Removing watched videos from course")
        unwatched_videos = []
        for i in range(0, len(status_span) - 1):
            status_text = status_span[i].find_element(By.XPATH, "./child::*").text
            if (status_text != 'WATCHED'):
                unwatched_videos.append(videos[i])

        links_hrefs = [link.get_attribute('href') for link in unwatched_videos]
        for i in range(0, len(links_hrefs) - 2):
            print(self.prefix + "Accessing video : " + video_titles[i])
            self.get_video(links_hrefs[i])
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".vjs-play-control.vjs-control.vjs-button")))
            play = self.browser.find_elements(By.CSS_SELECTOR, '.vjs-play-control.vjs-control.vjs-button')
            play[0].click()
            sleep(1)
            play[0].send_keys(Keys.PAGE_DOWN)

            # Gotta go fast
            self.browser.find_element('id', 'video-player-settings-button').click()

            sleep(1)

            self.browser.find_element('id', 'speed').click()

            sleep(1)

            self.browser.find_element("xpath", "//span[@id='current_value_prefix'][text()='2']").click()
            print(self.prefix + "Watching video with double speed")

            duration = self.browser.find_element(By.CLASS_NAME, "vjs-duration-display").text
            duration_seconds = (sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(duration.split(":")))) + 5) / 2
            print(self.prefix + "Sleeping until end of video for current course for " + str(duration_seconds) + " "
                                                                                                                "seconds")
            sleep(duration_seconds)
            print(self.prefix + "Finished watching the video " + video_titles[i])
        print(self.prefix + "Videos for current course watched")
        return links_hrefs[1]

    def get_course_name(self):
        return self.browser.find_element(By.CLASS_NAME, "MediaTitleV2---titleHeader---xIfCJ").text

    def get_completion_status(self) -> bool:
        div_completion_all = self.browser.find_element_by_xpath("//div[@class='ProgressBar---trail---3y2hW']")

        div_completion_status = self.browser.find_element_by_xpath("//div[@class='ProgressBar---stroke---1w8-k']")

        total_width = div_completion_all.value_of_css_property('width')

        actual_width = div_completion_status.value_of_css_property('width')

        return actual_width == total_width

    def pass_test(self) -> bool:
        print(self.prefix + "Starting test")
        test_answers = []
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-marker='takeTestFromAssessmentLaunchPage']"))).click()

        WebDriverWait(self.browser, 3).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-marker='courseAssessmentStart']"))).click()
        end_test = False
        while not end_test:
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "LabeledMessage---labeledMessage---1qn6X")))
            question = self.browser.find_element(By.CLASS_NAME, "LabeledMessage---labeledMessage---1qn6X").text.strip()
            instruction = self.browser.find_element(By.XPATH,
                                                    "//div[@class='MessageBar---instruction---3-J99']").text.strip()
            answers = []
            print(self.prefix +"Finding answers for " + question)
            if instruction == "Instruction: Choose the option that best answers the question.":
                self.find_radio_answers(answers, question, test_answers)
            elif instruction == "Instruction: Choose all options that best answer the question.":
                self.find_checkbox_answers(answers, question, test_answers)
            else:
                options = self.browser.find_elements(By.XPATH, "//ul[@class='Matching---ul---bIrQZ']")[0].text.split("\n")
                letter_answer_map = {}
                for i in range(1, len(options)):
                    split_text = options[i].split(":")
                    letter_answer_map[split_text[0]] = split_text[1]
                print(letter_answer_map)
                options = self.browser.find_elements(By.CLASS_NAME, "Matching---choiceTitle---3ENuZ")
                print(options[0].find_element(By.XPATH,
                                                                      "./child::*").text)
                for i in range(0, len(options)):
                    print(self.prefix + options[i].text)
                options_by_category = self.browser.find_elements(By.CSS_SELECTOR,
                                                                ".Checkbox---checkboxContainer---2Hz1S."
                                                                      "Checkbox---spaced---1d8os")
                for i in range(0, len(options_by_category)):
                    print(options_by_category[i].text)
                exit()
        test_passed = False
        if test_passed is False:
            self.pass_test()

        print(self.prefix + "Fin du test")
        return True

    def find_checkbox_answers(self, answers, question, test_answers):
        options = self.browser.find_elements(By.CSS_SELECTOR, ".Checkbox---checkboxContainer---2Hz1S."
                                                              "Checkbox---spaced---1d8os")
        text_options = []
        for i in range(0, len(options)):
            text_options.append(options[i].text)
        options[0].click()
        self.verify_answers()
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ValidationMark---multipleChoiceAnswer---AWXKG")))
        possible_answers = self.browser.find_elements(By.CLASS_NAME, "ValidationMark---multipleChoiceAnswer---AWXKG")
        for i in range(0, len(possible_answers)):
            if "Sorry, you should have selected this option." in possible_answers[
                i].text.strip() or "Good job, you selected this correct option." in possible_answers[i].text:
                answers.append(text_options[i])
        this_question = {"question": copy(question), "answers": copy(answers)}
        test_answers.append(this_question)
        answers.clear()
        next_question_button = self.browser.find_element(By.XPATH, "//button[@data-marker='LP.assessments.next']")
        next_question_button.click()

    def find_radio_answers(self, answers, question, test_answers):
        options = self.browser.find_elements(By.CSS_SELECTOR, ".RadioButton---label---1dtPw."
                                                              "RadioButton---spaced---aeCFF")
        text_options = []
        for i in range(0, len(options)):
            text_options.append(options[i].text)
        ActionChains(self.browser).move_to_element(options[0]).click().perform()
        self.verify_answers()
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".Question---option---UEIWm.Question---correct---HaOFo")))
        answer = self.browser.find_element(By.CSS_SELECTOR,
                                           ".Question---option---UEIWm.Question---correct---HaOFo").text.strip()
        for i in range(0, len(options)):
            if options[i].text.strip() == answer:
                answers.append(text_options[i])
        this_question = {"question": copy(question), "answers": copy(answers)}
        test_answers.append(this_question)
        answers.clear()
        next_question_button = self.browser.find_element(By.XPATH, "//button[@data-marker='LP.assessments.next']")
        next_question_button.click()

    def verify_answers(self):
        self.browser.find_element(By.XPATH, "//button[@data-marker='LP.assessments.verify']").click()