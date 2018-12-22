# Developer  : ILYAS KERBAL
# Github: https://github.com/ilyasKerbal
# Email: kerbalsc@gmail.com

#Imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from DataModel import *
import os
import time
import pickle
import csv
import re

# Linkedin Web Driver Class
class LinkedInWebDriver(webdriver.Chrome):

    # Class Configuartion
    output_file = "profiles.csv"
    input_file = "profile_final.csv"

    def __init__(self, mode = "search"):
        # initiate the super class
        super().__init__()

        # this field is used to detect the last page
        self.if_last = False

        # Print current working directory
        print(os.getcwd())

        # This steep is crucial - Login verification and cookies settings
        cookies = []
        self.get("http://www.google.com")
        _ = input("Please press enter when window is fully loaded : ")
        # The window must be fully loaded to set cookies otherwise the app will crash!!
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
        except Exception as e:
            print(e) # First time You need to login in order to store cookies

        for cookie in cookies:
            self.add_cookie(cookie)
            print(cookie)

        if len(cookies) == 0:
            # No cookies found on pkl file, you need to login
            self.get("http://www.linkedin.com")
            pass_test = input("Enter after login : ")
            pickle.dump(self.get_cookies(), open("cookies.pkl", "wb"))
        if mode == "search":
        # Output file initialisation
            output = open(LinkedInWebDriver.output_file, mode="w")
            _ = csv.writer(output).writerow(['Name', 'Username', 'Url'])
            output.close()

        self.next_btn = None

    def scroll_down_slowly(self):
        # This method is used to scroll down slowly to load all profiles in the page
        check_height = self.execute_script("return document.body.scrollHeight;")

        #  Total height => 8 'chunks / parts'
        scroll_amount = check_height / 6
        for i in range(1, 7):
            time.sleep(0.5)
            self.execute_script("window.scrollTo(0, " + str(i * scroll_amount) + ");")
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.sleep_for(1)

    def scroll_up_slowly(self):
        check_height = self.execute_script("return document.body.scrollHeight;")
        scroll_amount = check_height / 6
        for i in reversed(range(6)):
            time.sleep(0.5)
            self.execute_script("window.scrollTo(0, " + str(i * scroll_amount) + ");")
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.sleep_for(1)

    def sleep_for(self, seconds):
        time.sleep(seconds)

    def profiles_list_scraper(self):
        with open(LinkedInWebDriver.output_file, mode="a") as output_file:
            csv_output = csv.writer(output_file)
            profiles_wrapper = self.find_elements(By.CLASS_NAME, 'search-result__wrapper')
            for wrapper in profiles_wrapper:
                url = wrapper.find_element(By.CSS_SELECTOR, "a[data-control-name='search_srp_result']")

                url_link = url.get_attribute("href")

                try:
                    url_name = wrapper.find_element(By.CSS_SELECTOR, "span .name").text
                except Exception:
                    break

                url_user = re.search('/([%\w\d-]+)/$', url_link, re.IGNORECASE)

                if url_user: url_user = url_user.group(1)
                else: url_user = "######"

                print(url_name, " - ", url_user, " - ", url_link)

                csv_output.writerow([url_name, url_user, url_link])

                self.implicitly_wait(3)

    def check_if_last_page(self):
        wait = WebDriverWait(self, 10)
        try:
            self.next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                   "button.next")))
        except Exception:
            self.if_last = True
        else:
            self.next_btn = self.find_element(By.CSS_SELECTOR,
                                          "button.next")

    def pages_scrap_profiles(self, urls):
        for url in urls:
            self.get(url)
            self.implicitly_wait(10)
            self.sleep_for(2)

            self.scroll_down_slowly()

            self.check_if_last_page()

            while not self.if_last:
                self.profiles_list_scraper()

                self.sleep_for(2)

                if not self.if_last: self.next_btn.click()

                self.implicitly_wait(12)
                time.sleep(2)
                self.scroll_down_slowly()

                self.implicitly_wait(12)
                self.sleep_for(1)

                self.check_if_last_page()

            if self.if_last :
                self.profiles_list_scraper()

                self.sleep_for(2)

                self.implicitly_wait(12)

                self.if_last = False

    def get_element_or_none_text(self, selector, classname):
        try:
            result = self.find_element(selector, classname).text
        except Exception:
            result = None
        finally:
            return result

    def get_skills_list(self):
        skills = []

        try:
            skills_elms = self.find_elements(By.CSS_SELECTOR, "p.pv-skill-category-entity__name")
        except Exception:
            print("Skills not found for this profile")
        else:
            for elm in skills_elms:
                skills.append(elm.text)
        return skills, len(skills)

    def get_element_inside_elment(self, element, selector, value):
        try:
            element_src = element.find_element(selector, value)
        except Exception as e:
            print(e)
            return None
        else:
            return element_src.text

    def get_experiences(self):
        experiences = []
        try:
            experiences_elm = self.find_element(By.CSS_SELECTOR, "section#experience-section.pv-profile-section")
        except Exception as e:
            print(e)
        else:
            try:
                experiences_items = experiences_elm.find_elements(By.CSS_SELECTOR, "div.pv-entity__summary-info")
            except Exception as e:
                print(e)
            else:
                for item in experiences_items:
                    to_add = {}
                    title = self.get_element_inside_elment(item, By.CSS_SELECTOR, "h3")
                    organisation = self.get_element_inside_elment(item, By.CSS_SELECTOR, "span.pv-entity__secondary-title")
                    date = self.get_element_inside_elment(item, By.CSS_SELECTOR, "h4.pv-entity__date-range span:not(.visually-hidden)")
                    location = self.get_element_inside_elment(item, By.CSS_SELECTOR, "h4.pv-entity__location span:not(.visually-hidden)")
                    duration = self.get_element_inside_elment(item, By.CSS_SELECTOR, ".pv-entity__bullet-item-v2")
                    to_add['title'] = title
                    to_add['organisation'] = organisation
                    to_add['date'] = date
                    to_add['location'] = location
                    to_add['duration'] = duration
                    experiences.append(to_add)

        return experiences

    def get_education(self):
        education = []
        try:
            education_elm = self.find_element(By.CSS_SELECTOR, "section#education-section")
        except Exception as e:
            print(e)
        else:
            try:
                education_items = education_elm.find_elements(By.CSS_SELECTOR, "div.pv-entity__summary-info")
            except Exception as e:
                print(e)
            else:
                for item in education_items:
                    to_add = {}
                    school = self.get_element_inside_elment(item, By.CSS_SELECTOR, "h3")
                    title = self.get_element_inside_elment(item, By.CSS_SELECTOR, "p.pv-entity__secondary-title span:not(.visually-hidden)")
                    date = self.get_element_inside_elment(item, By.CSS_SELECTOR, "p.pv-entity__dates span:not(.visually-hidden)")
                    to_add['school'] = school
                    to_add['title'] = title
                    to_add['date'] = date
                    education.append(to_add)

        return education

    def get_volunteer_activities(self):
        activities = []

        try:
            volunteer_elm = self.find_element(By.CSS_SELECTOR, "section.volunteering-section")
        except Exception as e:
            print(e)
        else:
            try:
                volunteer_items = volunteer_elm.find_elements(By.CSS_SELECTOR, "div.pv-entity__summary-info")
            except Exception as e:
                print(e)
            else:
                to_add = {}
                for item in volunteer_items:
                    title = self.get_element_inside_elment(item, By.CSS_SELECTOR, "h3")
                    description = self.get_element_inside_elment(item, By.CSS_SELECTOR, "span.pv-entity__secondary-title")
                    date = self.get_element_inside_elment(item, By.CSS_SELECTOR, "h4.pv-entity__date-range span:not(.visually-hidden)")
                    to_add['title'] = title
                    to_add['description'] = description
                    to_add['date'] = date
                    activities.append(to_add)
        return activities

    def scrap_profiles_data_to_DB(self):
        with open("profile_final.csv", "r") as file:
            csv_input = csv.DictReader(file)

            for row in csv_input:
                name = row["Name"]
                username = row["Username"]
                url = row["Url"]

                print(url)

                self.get(url)

                self.implicitly_wait(20)

                self.sleep_for(2)

                self.scroll_down_slowly()

                self.implicitly_wait(4)

                self.scroll_up_slowly()

                p_description = self.get_element_or_none_text(By.CSS_SELECTOR, "h2.pv-top-card-section__headline")
                p_location = self.get_element_or_none_text(By.CSS_SELECTOR, "h3.pv-top-card-section__location")
                p_last_school = self.get_element_or_none_text(By.CSS_SELECTOR, "span.pv-top-card-v2-section__entity-name.pv-top-card-v2-section__school-name")
                p_connections = self.get_element_or_none_text(By.CSS_SELECTOR, "span.pv-top-card-v2-section__connections")
                p_cuurent_job = self.get_element_or_none_text(By.CLASS_NAME, "span.pv-top-card-v2-section__company-name")
                p_connections_number = None

                try:
                    connection_number_Search = re.findall(r'\d+', p_connections)
                except Exception:
                    pass
                else:
                    p_connections_number = int(connection_number_Search[0])
                print(name, p_description, p_location, p_last_school, p_connections, p_connections_number)

                # Click "Show More" to display all data
                try:
                    # Skills
                    show_more = self.find_element(By.CSS_SELECTOR, "button.pv-skills-section__additional-skills.artdeco-container-card-action-bar")
                except Exception as e:
                    print(e)
                else:
                    show_more.send_keys(webdriver.common.keys.Keys.SPACE)
                    self.implicitly_wait(3)

                skills, len_skills = self.get_skills_list()
                print(skills)

                print(self.get_experiences())
                print(self.get_education())
                print(self.get_volunteer_activities())

                db.connect()
                profile_obj, _ = Profile.get_or_create(name=name, username=username, description=p_description, location=p_location, current_job=p_cuurent_job, last_school= p_last_school, connections_number=p_connections_number, skills_number=len_skills)

                for skill in skills:
                    skill_obj, _ = Skills.get_or_create(skill_name=skill)
                    HasSkill(user=profile_obj, skill=skill_obj).save()

                for experience in self.get_experiences():
                    t_title = experience['title']
                    t_organisation = experience['organisation']
                    t_date = experience['date']
                    t_location = experience['location']
                    t_duration = experience['duration']

                    print(t_title, t_organisation, t_date, t_location, t_duration)

                    organisation_obj, _ = Organisation.get_or_create(name=t_organisation)
                    HasExperience(user = profile_obj, organisation = organisation_obj, title = t_title, date = t_date, location = t_location, duration = t_duration).save()

                for education in self.get_education():
                    e_school = education['school']
                    e_title = education['title']
                    e_date = education['date']

                    school_obj, _ = School.get_or_create(name=e_school)
                    Studied(user = profile_obj, school = school_obj, title = e_title, date = e_date).save()

                for volunteer in self.get_volunteer_activities():
                    v_title = volunteer['title']
                    v_description = volunteer['description']
                    v_date = volunteer['date']

                    association_obj, _ = Association.get_or_create(name=v_description)

                    VolunteeredAt(user = profile_obj, association = association_obj, title = v_title, date = v_date).save()

                db.close()

