import os, sys
import requests
import time
import yaml
import pyperclip
from lxml import etree
from webcolors import name_to_hex
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


"""Chromedriver Initialization."""

with open("config/config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)
user_data_dir = config['USER_DATA_DIR']

WAIT_TIME = 2
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={user_data_dir}")
driver = webdriver.Chrome(chrome_options=options)
driver.maximize_window()
actions = ActionChains(driver)


"""Utility Functions Definition."""

def start_driver(main_url):
    driver.get(main_url)
    driver.implicitly_wait(2)


def close_driver():
    current_url = driver.current_url
    driver.quit()
    return current_url


def get_html_elements(xpath_="*"):
    """Returns list of web elements given xpath. Overwrite based on browserpilot."""

    elements = []
    html = driver.find_element(By.TAG_NAME, "html")
    html_string = html.get_attribute("outerHTML")

    object = etree.HTML(html_string)
    nodes = object.xpath(f"//{xpath_}")

    for node in nodes:
        element = etree.tostring(node).decode("utf-8")
        elements.append(element)

    return elements


def highlight_element(element):
    actions.move_to_element(element).perform()
    driver.execute_script("arguments[0].style.border = '3px solid red'", element)
    time.sleep(3)
    driver.execute_script("arguments[0].style.border = 'none'", element)


def get_elements_by_class(class_name):
    for _ in range(3):
        try:
            class_elements = driver.find_elements(By.CLASS_NAME, class_name)
            if not class_elements:
                print(f'RETRY -> get_elements_by_class EMPTY {class_name}')
                continue
            return class_elements
            break
        except:
            time.sleep(1)
            print(f'RETRY -> get_elements_by_class {class_name}')
            continue
    return class_elements


def get_elements_by_text(text):
    for _ in range(3):
        try:
            text_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            if not text_elements:
                print(f'RETRY -> get_elements_by_text EMPTY {text}')
                continue
            return text_elements
            break
        except:
            time.sleep(1)
            print(f'RETRY -> get_elements_by_text {text}')
            continue
    return text_elements


def select_project_button(project_name):
    for _ in range(3):
        try:
            project_text = driver.find_elements(By.XPATH, f"//*[contains(text(), '{project_name}')]")[1]
            project_button = project_text.find_elements(By.XPATH, "../../../../..")[0]
            return project_button
            break
        except:
            time.sleep(1)
            print('RETRY -> select_project_button')
            continue
        print('FAILED after 3 retry -> select_project_button')


def get_correct_caption(caption_text):
    try:
        url = "https://typewise-ai.p.rapidapi.com/correction/whole_sentence"
        payload = {
            "text": f"{caption_text}",
            "keyboard": "QWERTY",
            "languages": ["en"]
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "74bb79dc33msha44626951febeaep178ca5jsn9398170d8fbc",
            "X-RapidAPI-Host": "typewise-ai.p.rapidapi.com"
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        corrected_text = response.json()["corrected_text"]
        
        return corrected_text
    except:
        return caption_text


"""Tool Functions Definition."""

def create_new_project(name):
    """Creates a new project.
    For example, to create a new project named 'My Vlog', should use: create_new_project('My Vlog')"""

    create_new_project = driver.find_elements(By.CLASS_NAME, "Folder-module_createText_-tw9f")[0]
    create_new_project.click()
    driver.implicitly_wait(2)


def open_project(name):
    """Open an existed project.
    For example, to open a project named 'My Vlog', should use: open_project('My Vlog')"""

    project_button = select_project_button(name)
    project_button.click()
    time.sleep(15)


def upload_video(local_dir):
    """Upload a video from given local directory.
    For example, to upload a video stored in '/User/Download/xxx.mp4', should use: upload_video('/User/Download/xxx.mp4')"""

    upload_button = driver.find_elements(By.CLASS_NAME, "Upload-module_uploadButton_5vs7h")[0]
    upload_button.send_keys(f"{local_dir}")
    driver.implicitly_wait(2)


def add_caption(caption_text):
    """Add the given caption to the video.
    For example, to add 'Coffee Time', should use: add_caption('Coffee Time')"""
    
    try:
        text_tab_button = get_elements_by_text("Text")[1]
        text_tab_button.click()

        add_text_button_sub = get_elements_by_text("Add Text")[0]
        add_text_button = add_text_button_sub.find_elements(By.XPATH, "..")[0]
        add_text_button.click()

        caption_element = get_elements_by_text("Sample text")[1]
        caption_element.send_keys([Keys.BACK_SPACE]*15, caption_text)

        global text_edit_tab, text_animate_tab, text_effects_tab, text_timing_tab

        text_edit_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[1]
        text_animate_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[2] 
        text_effects_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[3]
        text_timing_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[4]

    except Exception as e:
        print(e)
        close_driver()


def change_caption_text(caption_text, timestamp):
    """Change caption's text given timestamp.
    For example, to change the caption content at 18 seconds to 'Happy Life', should use: change_caption_text('Happy Life', 18)"""
    
    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    layers = get_elements_by_class("common-module_controlSectionRow_u6iL8")

    fit_to_screen = get_elements_by_text("Fit")[0]
    fit_to_screen.click()

    gap_pixels = 15
    multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
    factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

    pixels = gap_pixels + (timestamp) * (multiplier_pixels / factor)

    slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
    driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
    slider.click()

    elements = get_elements_by_class("Transformer-module_transformer_AgKxF")
    for ele in elements:
        try:
            ele.click()

            edit_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[1]
            edit_tab.click()

            if get_elements_by_class("common-module_controlSectionTitle_eK-7P")[0].text == "Font":
                actions.move_to_element(ele).click().send_keys([Keys.BACK_SPACE]*100, caption_text).perform()
        except:
            pass

    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()


def change_caption_time(start_time, end_time):
    """Change the caption's timestamp given start time and end time.
    For example, to change caption starting from 5 second and ending at 10 second, should use: change_caption_time(5, 10)"""

    text_timing_tab.click()

    start_mins_box = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")[0]
    start_seconds_box = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")[1]
    end_mins_box = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")[3]
    end_seconds_box = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")[4]

    default_end_seconds = int(end_seconds_box.text)
    end_keys = end_time - default_end_seconds
    default_start_seconds = int(start_seconds_box.text)
    start_keys = start_time - default_start_seconds

    end_seconds_box.click()
    actions.send_keys([Keys.ARROW_UP]*end_keys).perform()

    start_seconds_box.click()
    actions.send_keys([Keys.ARROW_UP]*start_keys).perform()

    text_edit_tab.click()


def change_caption_style(style_name):
    """Change the caption's style.
    For example, to change the style of the caption to 'italic', should use: change_caption_style('italic')"""

    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    bold_button = get_elements_by_class("common-module_smallControlButton_66vuT")[1]
    italic_button = get_elements_by_class("common-module_smallControlButton_66vuT")[2]
    underline_button = get_elements_by_class("common-module_smallControlButton_66vuT")[3]

    if style_name == 'bold':
        bold_button.click()
        
    if style_name == 'italic':
        italic_button.click()
        
    if style_name == 'underline':
        underline_button.click()


def change_caption_color(color):
    """Change the caption's color. Color must be provided in hex code.
    For example, to change caption's color to red, should use: change_caption_color('FF0000')"""

    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    color_box_button = get_elements_by_class("common-module_smallControlButton_66vuT")[7]
    color_box_button.click()

    color_box_text_element = get_elements_by_class("ColorInput-module_colorInput_u7idt")[0]
    color_box_text_element.send_keys([Keys.BACK_SPACE]*10, color, Keys.ENTER)

    continue_button = get_elements_by_class("LayerColorSelector-module_bottom_XEq1i")[0]
    continue_button.click()


def change_caption_font_size(font_size):
    """Change the caption's font size.
    For example, to change the caption size to 64, should use: change_caption_font_size(64)"""
    
    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    font_size_button = get_elements_by_class("common-module_dropdownDirectInput_m4-FD")[0]
    font_size_button.click()
    font_size_button.send_keys(Keys.BACK_SPACE, Keys.BACK_SPACE, font_size)

    text_edit_tab.click()


def change_caption_font_type(font):
    """Change the caption's font type.
    For example, to change the caption font to 'Times New Roman', should use: change_caption_font_type('Times New Roman')"""

    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    try:
        font_type_button = get_elements_by_text("Impact")[0].click()
        font_type_button.click()
        font_type = get_elements_by_text(font)[0]
        font_type.click()
    except:
        text_edit_tab.click()
        pass


def change_caption_outline_color(color):
    """Change the caption's outline color. Color must be provided in hex code.
    For example, to change caption outline color to red, should use: change_caption_outline_color('FF0000')"""
    
    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    text_outline_button = get_elements_by_class("common-module_smallControlButton_66vuT")[8]
    text_outline_button.click()

    color_box_text_element = get_elements_by_class("ColorInput-module_colorInput_u7idt")[0]
    color_box_text_element.send_keys([Keys.BACK_SPACE]*15, color, Keys.ENTER)

    continue_button = get_elements_by_class("LayerColorSelector-module_bottom_XEq1i")[0]
    continue_button.click()


def change_caption_background_color(color):
    """Change the caption's background color. Color must be provided in hex code.
    For example, to change caption background color to blue, should use: change_caption_background_color('0000FF')"""

    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    text_back_button = get_elements_by_class("common-module_smallControlButton_66vuT")[9]
    text_back_button.click()

    color_box_text_element = get_elements_by_class("ColorInput-module_colorInput_u7idt")[0]
    color_box_text_element.send_keys([Keys.BACK_SPACE]*15, color, Keys.ENTER)

    continue_button = get_elements_by_class("LayerColorSelector-module_bottom_XEq1i")[0]
    continue_button.click()


def change_caption_opacity(opacity):
    """Change the caption's opacity.
    For example, to change the caption opacity to 70, should use: change_caption_opacity(70)"""

    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    opactiy_dec_button = get_elements_by_class("common-module_incrementDecrementButton_gr5Cg")[0]

    if opacity != 100:
        opacity_decrease = (100 - opacity) // 10
    
        for i in range(opacity_decrease):
            opactiy_dec_button.click()

    text_edit_tab.click()

 
def change_caption_position(x_pos, y_pos):
    """Change the caption's position.
    For example, to move the caption down by 4 and right by 6, should use: change_caption_position(6, -4)"""

    text_tab_button = get_elements_by_text("Text")[1]
    text_tab_button.click()

    x_pos_box = driver.find_elements(By.CSS_SELECTOR,"input[data-testid='layer-position-control__x-input']")[0]
    x_pos_box.send_keys([Keys.BACK_SPACE]*10, x_pos)

    y_pos_box = driver.find_elements(By.CSS_SELECTOR,"input[data-testid='layer-position-control__y-input']")[0]
    y_pos_box.send_keys([Keys.BACK_SPACE]*10, y_pos)

    text_edit_tab.click()


def delete_row(layer_id):
    """Delete any layer row.
    For example, to delete the 3rd row, should use: delete_row(3)"""

    layers_button = get_elements_by_text("Layers")[0]
    layers_button.click()

    layers = get_elements_by_class("TimelineRows-module_timelineRowText_yHt8c")
    layer_objects = get_elements_by_class("Track-module_container_mph21")

    layer_elements = get_elements_by_class("common-module_controlSectionRow_u6iL8")

    del_layer_element = layers[layer_id - 1]
    actions.context_click(del_layer_element).perform()

    del_row_button = get_elements_by_text("Delete row")[0]
    del_row_button.click()

    del_confirm_button = get_elements_by_class("OverlayContent-module_primaryButton_FZkdT")[0]
    del_confirm_button.click()


def add_row_above(layer_id):
    """Add empty row above any layer.
    For example, to add an empty row above the 2nd layer, should use: add_row_above(2)"""

    layers_button = get_elements_by_text("Layers")[0]
    layers_button.click()

    layers = get_elements_by_class("TimelineRows-module_timelineRowText_yHt8c")
    layer_objects = get_elements_by_class("Track-module_container_mph21")

    add_row_layer_element= layers[layer_id - 1]
    actions.context_click(add_row_layer_element).perform()
    add_row_button = get_elements_by_text("Add row")[0]
    add_row_button.click()


def detach_audio():
    """Detach audio from main video.
    For example, to detach audio from main video, should use: detach_audio()"""

    layers_button = get_elements_by_text("Layers")[0]
    layers_button.click()

    layers = get_elements_by_class("TimelineRows-module_timelineRowText_yHt8c")
    layer_objects = get_elements_by_class("Track-module_container_mph21")

    actions.context_click(layer_objects[0]).perform()
    detach_button = get_elements_by_text("Detach")[1]
    detach_button.click()


def show_layer_info():
    """Show all layers information.
    Should use: show_layer_info()"""

    layers_button = get_elements_by_text("Layers")[0]
    layers_button.click()

    layer_elements = get_elements_by_class("common-module_controlSectionRow_u6iL8")

    for layer in layer_elements:
        print(layer.text)


def delete_layer(layer_id):
    """Delete any layer.
    For example, to delete the 3rd layer, should use: delete_layer(3)"""
    
    del_layer_button = get_elements_by_class("Controls-module_layerControlRight_p7h1D")[layer_id - 1]
    del_layer_button.click()


def trim_video(start_timestamp, end_timestamp):
    """Trim the video clip given start timestamp and end timestamp.
    For example, to trim the video starting from 2 and ending at 6, should use: trim_video(2, 6)"""

    time.sleep(WAIT_TIME)
    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    video_layers = {}
    idx = 0 
    layers = get_elements_by_class("common-module_controlSectionRow_u6iL8")

    for layer in layers:
        layer.click()
        edit_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[1]
        edit_tab.click()
        if get_elements_by_class("common-module_controlSectionTitle_eK-7P")[0].text == "Video":
            video_layers[idx]  = layer
            idx += 1  
            
    l = len(video_layers) - 1 
    start_sec = int(str(start_timestamp).split(".")[0])
    start_mili_sec = int(str(start_timestamp).split(".")[1])

    end_sec = int(str(end_timestamp).split(".")[0])
    end_mili_sec = int(str(end_timestamp).split(".")[1])*10
    for i in range(len(video_layers)):
        video_layers[l - i].click()
        
        trim_button = get_elements_by_text("Trim")[0]
        trim_button.click()
        
        
        layer_start_sec = get_elements_by_class("ExactInputBox-module_input_ezpNr")[1].get_attribute("value")
        layer_start_mili = get_elements_by_class("ExactInputBox-module_input_ezpNr")[2].get_attribute("value")
        layer_start = float(f"{int(layer_start_sec)}.{int(layer_start_mili)}")
        
        
        layer_end_sec = get_elements_by_class("ExactInputBox-module_input_ezpNr")[4].get_attribute("value")
        layer_end_mili = get_elements_by_class("ExactInputBox-module_input_ezpNr")[5].get_attribute("value")
        layer_end = float(f"{int(layer_end_sec)}.{int(layer_end_mili)}")
        

        if start_timestamp > layer_start:
            get_elements_by_class("ExactInputBox-module_input_ezpNr")[1].send_keys(start_sec)
            get_elements_by_class("ExactInputBox-module_input_ezpNr")[2].send_keys(start_mili_sec)
        elif end_timestamp < layer_end: 
            get_elements_by_class("ExactInputBox-module_input_ezpNr")[4].send_keys(end_sec)
            get_elements_by_class("ExactInputBox-module_input_ezpNr")[5].send_keys(end_mili_sec)

        trim_button = get_elements_by_text("Trim")[-1]
        trim_button.click()
        
    video_layers[len(video_layers) -1 ].click()
    time_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[4]
    time_tab.click()

    time_buttons = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")
            
    end_time_sec = int(time_buttons[4].text)
    end_time_mili = int(time_buttons[5].text)

    layer_end_time= float(f"{end_time_sec}.{end_time_mili}")

    for i in range(1, len(video_layers)):
        video_layers[l - i].click()
        time_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[4]
        time_tab.click()
        time_buttons = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")
        
        start_time_sec = int(time_buttons[1].text)
        start_time_mili = int(time_buttons[2].text)

        start_time = float(f"{start_time_sec}.{start_time_mili}")
        end_time_sec = int(time_buttons[4].text)
        end_time_mili = int(time_buttons[5].text)

        end_time= float(f"{end_time_sec}.{end_time_mili}")
        
        layer_length = end_time - start_time 
        layer_start_time = layer_end_time
        layer_end_time = layer_start_time + layer_length

        
        fit_to_screen = get_elements_by_text("Fit")[0]
        fit_to_screen.click()

        gap_pixels = 15
        multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
        factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

        pixels = gap_pixels + (layer_start_time)*(multiplier_pixels/ factor)

        slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
        driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
        slider.click()
        
        start_set = get_elements_by_text("Set to")[0]
        start_set.click()  

        fit_to_screen = get_elements_by_text("Fit")[0]
        fit_to_screen.click()

        gap_pixels = 15
        multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
        factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

        pixels = gap_pixels + (layer_end_time)*(multiplier_pixels/ factor)

        slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
        driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
        slider.click()
        
        end_set = get_elements_by_text("Set to")[1]
        end_set.click()
        
    remaining_layers = {}
    idx = 0 
    layers = get_elements_by_class("common-module_controlSectionRow_u6iL8")

    for layer in layers:
        layer.click()
        edit_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[1]
        edit_tab.click()
        if get_elements_by_class("common-module_controlSectionTitle_eK-7P")[0].text != "Video":
            remaining_layers[idx]  = layer
            idx += 1  
            
    for i in range(len(remaining_layers)):
        remaining_layers[i].click()
        time_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[4]
        time_tab.click()
        time_buttons = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")
        
        start_time_sec = int(time_buttons[1].text)
        start_time_mili = int(time_buttons[2].text)

        start_time = float(f"{start_time_sec}.{start_time_mili}")
        end_time_sec = int(time_buttons[4].text)
        end_time_mili = int(time_buttons[5].text)

        end_time= float(f"{end_time_sec}.{end_time_mili}")

        if start_time < start_timestamp:
            fit_to_screen = get_elements_by_text("Fit")[0]
            fit_to_screen.click()

            gap_pixels = 15
            multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
            factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

            pixels = gap_pixels + (end_time - start_timestamp)*(multiplier_pixels/ factor)

            slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
            driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
            slider.click()
            end_set = get_elements_by_text("Set to")[1]
            end_set.click()
            break
            time.sleep(WAIT_TIME)

        elif end_time > end_timestamp:
            fit_to_screen = get_elements_by_text("Fit")[0]
            fit_to_screen.click()

            gap_pixels = 15
            multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
            factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

            pixels = gap_pixels + (start_time -start_timestamp)*(multiplier_pixels/ factor)

            slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
            driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
            slider.click()

            start_set = get_elements_by_text("Set to")[0]
            start_set.click()  

            fit_to_screen = get_elements_by_text("Fit")[0]
            fit_to_screen.click()

            gap_pixels = 15
            multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
            factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

            pixels = gap_pixels + (end_timestamp - start_timestamp)*(multiplier_pixels/ factor)

            slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
            driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
            slider.click()

            end_set = get_elements_by_text("Set to")[1]
            end_set.click()
        else:
            fit_to_screen = get_elements_by_text("Fit")[0]
            fit_to_screen.click()

            gap_pixels = 15
            multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
            factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

            pixels = gap_pixels + (start_time -start_timestamp)*(multiplier_pixels/ factor)

            slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
            driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
            slider.click()

            start_set = get_elements_by_text("Set to")[0]
            start_set.click()  

            fit_to_screen = get_elements_by_text("Fit")[0]
            fit_to_screen.click()

            gap_pixels = 15
            multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
            factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

            pixels = gap_pixels + (end_time -start_timestamp)*(multiplier_pixels/ factor)

            slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
            driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
            slider.click()

            end_set = get_elements_by_text("Set to")[1]
            end_set.click()


def add_audio(audio_path, timestamp):
    """Add audio clip at given timestamp with audio path.
    For example, to add an audio file '/User/Downloads/music.mp3' at 12 second, should use: add_audio('/User/Downloads/music.mp3', 12)"""

    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    pixels = 15 + (timestamp)*20
    slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
    driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
    slider.click()

    audio_tab_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Audio')]")[0]
    audio_tab_button.click()

    upload_button = get_elements_by_class("Upload-module_uploadButton_5vs7h")[0]
    upload_button.send_keys(f"{audio_path}")


def change_volume(volume):
    """Change the video's volume from 0% to 200%.
    For example, to update the video volume to 80%, should use: change_volume(80)
    """

    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    audio_layer = get_elements_by_class("common-module_controlSectionRow_u6iL8")[0]
    audio_layer.click()

    edit_tab = get_elements_by_text("edit")[1]
    edit_tab.click()

    volume_slider = get_elements_by_class("common-module_controlSlider_d0JZw")[0]
    driver.execute_script(f"arguments[0].value = '{volume/100}';", volume_slider)
    driver.execute_script(f"arguments[0].value = '{volume/100}';", volume_slider)


def add_image(image_location, start_timestamp, end_timestamp):
    """Add an image banner at given start and end timestamp with audio path.
    For example, to add an image file '/User/Downloads/pic.jpg' at 7 second, should use: add_image('/User/Downloads/pic.jpg', 7)"""
    
    time.sleep(WAIT_TIME)
    layers_button = get_elements_by_text('Layers')[0]
    layers_button.click()

    fit_to_screen = get_elements_by_text("Fit")[0]
    fit_to_screen.click()

    gap_pixels = 15
    multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
    factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

    pixels = gap_pixels + (start_timestamp)*(multiplier_pixels/ factor)

    slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
    driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
    slider.click()

    media_tab = get_elements_by_text("Media")[0]
    media_tab.click()

    add_media = get_elements_by_class("CloudMediaLibraryTile-module_addContainer_Mppgd")[0]
    add_media.click()

    upload_button = get_elements_by_class("Upload-module_uploadButton_5vs7h")[0]
    upload_button.send_keys(image_location)

    image_media = get_elements_by_class("CloudMediaLibraryTile-module_container_kssdy")[1]
    image_media.click()
    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    image_layer = get_elements_by_class("common-module_controlSectionRow_u6iL8")[0]
    image_layer.click()

    edit_tab = get_elements_by_text("edit")[1]
    edit_tab.click()

    zoom_slider = get_elements_by_class("common-module_controlSlider_d0JZw")[0]
    actions.move_to_element(zoom_slider).click_and_hold()
    actions.move_by_offset(0, 0).perform()
    actions.release().perform()

    gap_pixels = 15
    multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
    factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

    pixels = gap_pixels + (end_timestamp)*(multiplier_pixels/ factor)

    slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
    driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
    slider.click()

    time_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[4]
    time_tab.click()
    time.sleep(WAIT_TIME)
    end_set = get_elements_by_text("Set to")[1]
    end_set.click()


def zoom_image(zoom_percentage):
    """Zoom in and zoom out the image banner with a range of 0% to 200%.
    For example, to zoom the image to 120% of its original size, should use: zoom_image(120)
    """

    time.sleep(WAIT_TIME)
    layers_button = get_elements_by_text('Layers')[0]
    layers_button.click()

    fit_to_screen = get_elements_by_text("Fit")[0]
    fit_to_screen.click()

    media_tab = get_elements_by_text("Media")[0]
    media_tab.click()

    image_media = get_elements_by_class("CloudMediaLibraryTile-module_container_kssdy")[1]
    image_media.click()
    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    image_layer = get_elements_by_class("common-module_controlSectionRow_u6iL8")[0]
    image_layer.click()

    edit_tab = get_elements_by_text("edit")[1]
    edit_tab.click()

    zoom_slider = get_elements_by_class("common-module_controlSlider_d0JZw")[0]
    slider_range = zoom_slider.size["width"]
    zoom_pixels = (zoom_percentage - 100)* int(slider_range/2) / 100

    actions.move_to_element(zoom_slider).click_and_hold()
    actions.move_by_offset(zoom_pixels, 0).perform()
    actions.release().perform()


def add_transition(timestamp, transition, speed):
    """Add transition to given timestamp, and set speed of transition to slow, default and fast.
    If speed is not mentioned, should set speed = 'default'.
    For example, to add a 'drop' transition with fast speed at 10 sec, should use: add_transition(10, 'drop', 'fast')"""

    time.sleep(WAIT_TIME)  
    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    video_layer = layers = get_elements_by_class("common-module_controlSectionRow_u6iL8")[-1]
    video_layer.click() 
    fit_to_screen = get_elements_by_text("Fit")[0]
    fit_to_screen.click()

    gap_pixels = 15
    multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
    factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

    pixels = gap_pixels + (timestamp)*(multiplier_pixels/ factor)

    slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
    driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
    slider.click()

    layer_objects = get_elements_by_class("Track-module_container_mph21")
    layer_objects[0].click()

    split_button = get_elements_by_text("Split")[1]
    split_button.click()

    transitions_button = get_elements_by_text("transitions")[0]
    transitions_button.click()

    transitions_dict = {}
    sub_transitions_elements = get_elements_by_class("TransitionControls-module_transitionRow_RsLG0")
    for elements in sub_transitions_elements:
        transitions_elements = elements.find_elements( By.TAG_NAME , "div")
        for i in range(0,4,2):
            transitions_dict[transitions_elements[i].text.lower()] = transitions_elements[i]

    try:
        transition_selection = transitions_dict[transition]
        transition_selection.click()
    except:
        print("select any of these transitions", list(transitions_dict.keys()))

    outro_button = get_elements_by_text("Outro")[0].find_elements(By.XPATH, "..")[0]
    outro_button.click()

    slow_button = get_elements_by_text("Slow")[0].find_elements(By.XPATH, "..")[0]
    default_button = get_elements_by_text("Default")[0].find_elements(By.XPATH, "..")[0]
    fast_button = get_elements_by_text("Fast")[0].find_elements(By.XPATH, "..")[0]

    if speed == "fast":
        fast_button.click()
    elif speed == "slow":
        slow_button.click()
    else:
        default_button.click()

    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()


def export_video(video_end_time):
    """Export the whole video given ending time.
    For example, to export or finish the video of 20 seconds in length, should use: export_video(20)"""

    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    video_element = get_elements_by_class("common-module_controlSectionRow_u6iL8")[-1]
    video_element.click()

    time_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[4]
    time_tab.click()

    time_buttons = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")

    end_time = int(time_buttons[3].text)*60 + int(time_buttons[4].text)

    end_seconds_box = get_elements_by_class("ExactInputBox-module_containerTimeBox_4sHbQ")[4]
    end_keys = end_time - video_end_time
    if end_keys> 0 :
        end_seconds_box.click()
        time.sleep(WAIT_TIME)
        actions.send_keys([Keys.ARROW_DOWN]*end_keys).perform()
        
    export_button = get_elements_by_text("Export")[0]
    export_button.click()

    export_as_mp4 = get_elements_by_text("Export")[2]
    export_as_mp4.click()

    time.sleep(WAIT_TIME)
    export_url = driver.current_url
    print(export_url)


def caption_spelling_correction(timestamp):
    """Correct the caption text at timestamp.
    For example, to correct the caption at 27 sec, should use: caption_spelling_correction(27)"""
    
    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()

    layers = get_elements_by_class("common-module_controlSectionRow_u6iL8")

    fit_to_screen = get_elements_by_text("Fit")[0]
    fit_to_screen.click()

    gap_pixels = 15
    multiplier_pixels = get_elements_by_class("TimeLabels-module_tick_fvLlX")[0].size['width']
    factor = int(get_elements_by_class("TimeLabels-module_tick_fvLlX")[1].text[-1])

    pixels = gap_pixels + (timestamp)*(multiplier_pixels/ factor)

    slider = get_elements_by_class("Seeker-module_seekerContainer_HkUsQ")[0]
    driver.execute_script(f"arguments[0].style.transform = 'translateX({pixels}px)';", slider)
    slider.click()

    elements = get_elements_by_class("Transformer-module_transformer_AgKxF")
    for ele in elements:
        try:
            ele.click()

            edit_tab = get_elements_by_class("Tabs-module_tab_HQZWB")[1]
            edit_tab.click()

            if get_elements_by_class("common-module_controlSectionTitle_eK-7P")[0].text == "Font":
                actions.move_to_element(ele).click().key_down(Keys.COMMAND).send_keys("a", "c").perform()
                caption_text = pyperclip.paste()

                caption_text = caption_text.replace("\r", "").replace("\n", "")
                updated_text = get_correct_caption(caption_text)
                print("Original Text = ", caption_text)
                print("Corrected Text = ", updated_text)
                actions.move_to_element(ele).click().key_down(Keys.COMMAND).send_keys("a", Keys.BACK_SPACE).key_up(Keys.COMMAND).send_keys(list(updated_text)).perform()
        except:
            
            pass
    layers_button = driver.find_elements(By.XPATH, "//*[contains(text(), 'Layers')]")[0]
    layers_button.click()


"""New selenium functions designed with selenium ide."""

def add_text(text: str):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(3) .MediaSidebar-module_mediaIcon_aF-LX').click()
    driver.find_element(By.CSS_SELECTOR, ".AddTextButton-module_addTextButton_oXsr8").click()
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    driver.find_element(By.CSS_SELECTOR, '.DraftEditor-editorContainer > .notranslate').send_keys([Keys.BACK_SPACE]*15, text)
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def change_text_color(color: str):
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_controlSectionContainer_7gwIs:nth-child(3) .common-module_smallControlButton_66vuT').click()
    driver.find_element(By.CSS_SELECTOR, '.ColorInput-module_colorInput_u7idt').click()
    color_hex_code = name_to_hex(color)
    driver.find_element(By.CSS_SELECTOR, '.ColorInput-module_colorInput_u7idt').send_keys([Keys.BACK_SPACE]*6)
    driver.find_element(By.CSS_SELECTOR, '.ColorInput-module_colorInput_u7idt').send_keys(color_hex_code)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '.LayerColorSelector-module_selectButton_xHU7A').click()

def change_specific_text_color(text: str, color: str):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(2) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_elements(By.XPATH, f'//*[contains(text(), "{text}")]')[0].click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_controlSectionContainer_7gwIs:nth-child(3) .common-module_smallControlButton_66vuT').click()
    driver.find_element(By.CSS_SELECTOR, '.ColorInput-module_colorInput_u7idt').click()
    color_hex_code = name_to_hex(color)
    driver.find_element(By.CSS_SELECTOR, '.ColorInput-module_colorInput_u7idt').send_keys([Keys.BACK_SPACE]*6)
    driver.find_element(By.CSS_SELECTOR, '.ColorInput-module_colorInput_u7idt').send_keys(color_hex_code)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '.LayerColorSelector-module_selectButton_xHU7A').click()
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def change_text_content(text: str):
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    # driver.find_element(By.CSS_SELECTOR, '.DraftEditor-editorContainer > .notranslate').clear()
    driver.find_element(By.CSS_SELECTOR, '.notranslate').clear()
    driver.find_element(By.CSS_SELECTOR, '.notranslate').send_keys(text)

def change_specific_text_content(text1: str, text2: str):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(2) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_elements(By.XPATH, f'//*[contains(text(), "{text1}")]')[0].click()
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    driver.find_element(By.CSS_SELECTOR, '.DraftEditor-editorContainer > .notranslate').clear()
    driver.find_element(By.CSS_SELECTOR, '.DraftEditor-editorContainer > .notranslate').send_keys(text2)
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def adjust_text_start_end_time(time1: int, time2: int):
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    driver.find_element(By.CSS_SELECTOR, '.Tabs-module_tab_HQZWB:nth-child(4)').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(1) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(1) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').send_keys(str(time1))
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').send_keys(str(time2))

def adjust_specific_text_start_end_time(text: str, time1: int, time2: int):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(2) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_elements(By.XPATH, f'//*[contains(text(), "{text}")]')[0].click()
    driver.find_element(By.CSS_SELECTOR, '.Tabs-module_tab_HQZWB:nth-child(4)').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(1) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(1) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').send_keys(str(time1))
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').send_keys(str(time2))
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def adjust_text_duration(time: int):
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    driver.find_element(By.CSS_SELECTOR, '.Tabs-module_tab_HQZWB:nth-child(4)').click()
    start_second = int(driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(1) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').text)
    end_second = time + start_second
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').send_keys(f'{end_second}')

def adjust_specific_text_duration(text: str, time: int):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(2) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_elements(By.XPATH, f'//*[contains(text(), "{text}")]')[0].click()
    driver.find_element(By.CSS_SELECTOR, '.Tabs-module_tab_HQZWB:nth-child(4)').click()
    start_second = int(driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(1) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').text)
    end_second = time + start_second
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').click()
    driver.find_element(By.CSS_SELECTOR, '.ExactInputBox-module_container_8ySEv:nth-child(2) .ExactInputBox-module_containerTimeBox_4sHbQ:nth-child(3) > .ExactInputBox-module_input_ezpNr').send_keys(f'{end_second}')
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def add_text_style(style_name: str):
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    dict = {'bold': '1', 'italic': '2', 'underline': '3'}
    driver.find_element(By.CSS_SELECTOR, f'.Text-module_textStyleControlsContainer_kkXjZ > .common-module_smallControlButton_66vuT:nth-child({dict[style_name]})').click()

def remove_text_style(style_name: str):
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    dict = {'bold': '1', 'italic': '2', 'underline': '3'}
    driver.find_element(By.CSS_SELECTOR, f'.Text-module_textStyleControlsContainer_kkXjZ > .common-module_smallControlButton_66vuT:nth-child({dict[style_name]})').click()

def add_specific_text_style(style_name: str, text: str):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(2) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_elements(By.XPATH, f'//*[contains(text(), "{text}")]')[0].click()
    dict = {'bold': '1', 'italic': '2', 'underline': '3'}
    driver.find_element(By.CSS_SELECTOR, f'.Text-module_textStyleControlsContainer_kkXjZ > .common-module_smallControlButton_66vuT:nth-child({dict[style_name]})').click()
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def remove_specific_text_style(style_name: str, text: str):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(2) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_elements(By.XPATH, f'//*[contains(text(), "{text}")]')[0].click()
    dict = {'bold': '1', 'italic': '2', 'underline': '3'}
    driver.find_element(By.CSS_SELECTOR, f'.Text-module_textStyleControlsContainer_kkXjZ > .common-module_smallControlButton_66vuT:nth-child({dict[style_name]})').click()
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def adjust_text_size(size: int):
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').send_keys(str(size))

def adjust_specific_text_size(text: str, size: int):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(2) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_elements(By.XPATH, f'//*[contains(text(), "{text}")]')[0].click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').send_keys(str(size))
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def increase_size():
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    font_size = int(driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').text)
    new_font_size = font_size + 10
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').send_keys(f'{new_font_size}')

def reduce_size():
    driver.find_element(By.CSS_SELECTOR, '.Transformer-module_selectedLayer_wuDY5').click()
    font_size = int(driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').text)
    new_font_size = font_size - 10
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').click()
    driver.find_element(By.CSS_SELECTOR, '.common-module_dropdownDirectInput_m4-FD').send_keys(f'{new_font_size}')

def add_sound_effect(keywords: str):
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(8) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()
    driver.find_element(By.CSS_SELECTOR, '.Search-module_tab_057MX:nth-child(2)').click()
    driver.find_element(By.CSS_SELECTOR, '.UploadSearchbar-module_darkThemeSearchBar_RBfE0').click()
    driver.find_element(By.CSS_SELECTOR, '.UploadSearchbar-module_darkThemeSearchBar_RBfE0').send_keys(keywords)
    driver.find_element(By.CSS_SELECTOR, '.UploadSearchbar-module_goButton_9BUyo').click()
    time.sleep(5)
    driver.find_elements(By.XPATH, '//div[@id=\'mediaSidebarControls\']/div/div/div[2]/div[2]/div[6]')[0].click()
    driver.find_element(By.CSS_SELECTOR, '.MediaSidebar-module_mediaSidebarIcon_cxxy2:nth-child(1) > .MediaSidebar-module_mediaSidebarIconSubheader_9EpxJ').click()

def test():
    start_driver(main_url=config['KAPWING_URL'])
    driver.implicitly_wait(2)
    open_project('Caption Test Project')
    time.sleep(5)
    _ = input("_")
    change_text_color("red")
    _ = input("_")
    change_specific_text_color("HELLO", "green")
    _ = input("_")
    change_text_content("HI")
    _ = input("_")
    change_specific_text_content("HI", "HELLO")
    _ = input("_")
    adjust_text_start_end_time(12, 15)
    print('Testing Successfully!')
    time.sleep(5)
    close_driver()

if __name__ == "__main__":
    test()