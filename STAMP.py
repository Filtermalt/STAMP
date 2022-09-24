from PIL import Image, ImageTk, ImageOps
import PySimpleGUI as sg
import re
import os


def main():
    #Initialize Start Variables
    logo_file_ok = False
    bck_dir_ok = False
    save_dir_ok = False
    x_ok = True
    y_ok = True
    s_ok = True
    image_index = 0
    sg.theme('black')
    layout = [
        [sg.Text("Logo Anchor Point"), sg.Spin([
        "Bottom Right", "Bottom Center", "Bottom Left",
        "Center Right", "Center", "Center Left",
        "Top Right", "Top Center", "Top Left",], text_color="black", size=(13, 1), readonly=True, key="-ANCHOR-"), sg.Text("Offset"),
        sg.Text("X", size=(1, 1)), sg.Input(text_color="#00ff00", size=(4, 1), default_text=5, enable_events=True, key="-X-"),
        sg.Text("Y:", size=(1, 1)), sg.Input(text_color="#00ff00", size=(4, 1), default_text=5, enable_events=True, key="-Y-"),
        
        sg.Text("Scale Logo Relative to Image"), sg.Spin(["Smallest", "Height", "Width"], text_color="black", size=(8, 1), readonly=True, key="-SCALING-"), sg.Text("Scale"), sg.Input(text_color="#00ff00", size=(4, 1), default_text=0.1, enable_events=True, key="-S-"),

        sg.Push(),
        sg.Button("<", disabled=True, key="-<-"), sg.Button(">", disabled=True, key="->-"), sg.Button("PREVIEW IMAGE", disabled=True, key="-REFRESH-")],

        [sg.Image(key='-IMAGE-')],

        [sg.Input(default_text=r"C:\Users\Kenneth\Pictures\STAMP3.png", size=(29, 1), enable_events=True, key="-LOGOFILE-"), sg.FileBrowse("Logo Path", key='-LOGO-'),
        sg.Input(default_text=r"C:\Users\Kenneth\Desktop\Magnus Navnefest - Copy", size=(29, 1), enable_events=True, key="-BCKFOLDER-"), sg.FolderBrowse("Image Dir"),
        sg.Input(default_text=r"C:\Users\Kenneth\Pictures\Images\StampedImages", size=(29, 1), enable_events=True, key="-SAVEFOLDER-"), sg.FolderBrowse("Save Dir"),
        sg.Push(), sg.Button("STAMP IMAGES", disabled=True, key="-START-")],
    ]
    window = sg.Window('STAMP', layout, icon="STAMP_ICON.ico",  margins=(0, 0), finalize=True)

    # Start GUI
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        # Start stamp process
        if event == "-START-":
            window["-REFRESH-"].update(disabled=True)
            window["-START-"].update(disabled=True)

            # Loop through all background images and STAMP them
            for i in range(len(bckgr_imgs)):

                img = Image.open(values["-BCKFOLDER-"] + "/" + bckgr_imgs[i])
                img = ImageOps.exif_transpose(img)
                name = bckgr_imgs[i].split("/")
                name = name[-1]

                # Calculate logo size
                logo_size = logo_relative_size(img, img_logo, values["-S-"], values["-SCALING-"])
                img_logo = img_logo.resize(logo_size, resample=1, box=None, reducing_gap=None)

                # Calculate location based on anchor and offset
                logo_location = make_logo_location(values["-X-"], values["-Y-"], img, img_logo, values["-ANCHOR-"])

                # Try to get alpha channel
                try:
                    img.paste(img_logo, logo_location, img_logo.getchannel(3))
                except ValueError:
                    img.paste(img_logo, logo_location)

                # Save at specified directory
                img.save(f'{values["-SAVEFOLDER-"]}/STAMPED_{name}')

            print(f"STAMP successfully STAMPED {len(bckgr_imgs)} images")
            window["-REFRESH-"].update(disabled=False)
            window["-START-"].update(disabled=False)

        # Changes preview image
        if event == "->-":
            print('>')
            image_index = image_index + 1
            print(image_index)
            event = "-REFRESH-"
        if event == "-<-":
            print('<')
            image_index = image_index - 1
            print(image_index)
            event = "-REFRESH-"

        # Preview image
        if event == "-REFRESH-":

            if image_index > (len(bckgr_imgs) -1):
                image_index = 0
            elif image_index < 0:
                image_index = len(bckgr_imgs) -1

            img = Image.open(values["-BCKFOLDER-"] + "/" + bckgr_imgs[image_index])
            img = ImageOps.exif_transpose(img)

            # Calculate logo size
            logo_size = logo_relative_size(img, img_logo, values["-S-"], values["-SCALING-"])
            img_logo = img_logo.resize(logo_size, resample=1, box=None, reducing_gap=None)

            # Calculate location based on anchor and offset
            logo_location = make_logo_location(values["-X-"], values["-Y-"], img, img_logo, values["-ANCHOR-"])
            
            # Try to get alpha channel
            try:
                img.paste(img_logo, logo_location, img_logo.getchannel(3))
            except ValueError:
                img.paste(img_logo, logo_location)
            
            # Create black image box
            image_box_size = 1000
            image_box = Image.new('RGB', (image_box_size, image_box_size), (0, 0, 0))
            
            # Sizing
            width, height = img.size
            if width > height:
                div_val = width / image_box_size
            else:
                div_val = height / image_box_size
            width = round(width / div_val)
            height = round(height / div_val)
            size = width, height
            loc_size = (round((image_box_size - width) * 0.5), round((image_box_size - height) * 0.5))
            img = img.resize(size, resample=1)
            image_box.paste(img, loc_size)

            # Convert and update image
            image = ImageTk.PhotoImage(image=image_box)
            window['-IMAGE-'].update(data=image)


        # Validate Numbers
        if event == "-X-":
            new_x = re.sub("[^0-9.-]", "", values["-X-"])
            new_x = re.sub(r"^\.", "", new_x)
            window["-X-"].update(new_x)
            try:
                float(new_x)
                x_ok = True
                window["-X-"].update(text_color="#00ff00")
            except ValueError:
                x_ok = False
                window["-X-"].update(text_color="#ff0000")

        if event == "-Y-":
            new_x = re.sub("[^0-9.-]", "", values["-Y-"])
            new_x = re.sub(r"^\.", "", new_x)
            window["-Y-"].update(new_x)
            try:
                float(new_x)
                y_ok = True
                window["-Y-"].update(text_color="#00ff00")
            except ValueError:
                y_ok = False
                window["-Y-"].update(text_color="#ff0000")

        if event == "-S-":
            new_x = re.sub("[^0-9.]", "", values["-S-"])
            new_x = re.sub(r"^\.", "", new_x)
            window["-S-"].update(new_x)
            try:
                if float(new_x) == 0:
                    float(new_x)
                    s_ok = False
                    window["-S-"].update(text_color="#ff0000")
                else:
                    float(new_x)
                    s_ok = True
                    window["-S-"].update(text_color="#00ff00")
            except ValueError:
                s_ok = False
                window["-S-"].update(text_color="#ff0000")

        # Validate all file paths
        if event == "-LOGOFILE-":
            if os.path.isfile(values["-LOGOFILE-"]):
                fn, fe = os.path.splitext(values["-LOGOFILE-"])
                if fe == ".jpg" or fe == ".jpeg" or fe == ".png":
                    try:
                        img_logo = Image.open(values["-LOGOFILE-"])
                        logo_file_ok = True
                        window["-LOGOFILE-"].update(text_color="#00ff00")
                    except FileNotFoundError:
                        logo_file_ok = False
                        window["-LOGOFILE-"].update(text_color="#ff0000")
                else:
                    logo_file_ok = False
                    window["-LOGOFILE-"].update(text_color="#ff0000")
            else:
                logo_file_ok = False
                window["-LOGOFILE-"].update(text_color="#ff0000")
        
        if event == "-BCKFOLDER-":
            if os.path.isdir(values["-BCKFOLDER-"]):
                bckgr_imgs = find_and_verify_images(values["-BCKFOLDER-"])
                if len(bckgr_imgs) > 0:
                    bck_dir_ok = True
                    window["-BCKFOLDER-"].update(text_color="#00ff00")  
                else:
                    bck_dir_ok = False
                    window["-BCKFOLDER-"].update(text_color="#ff0000")
            else:
                bck_dir_ok = False
                window["-BCKFOLDER-"].update(text_color="#ff0000")

        if event == "-SAVEFOLDER-":
            if os.path.isdir(values["-SAVEFOLDER-"]):
                save_dir_ok = True
                window["-SAVEFOLDER-"].update(text_color="#00ff00") 
            else:
                save_dir_ok = False
                window["-SAVEFOLDER-"].update(text_color="#ff0000")

        # Check if all is validated
        if event == "-X-" or event == "-Y-" or event == "-S-" or event == "-LOGOFILE-" or event == "-BCKFOLDER-" or event == "-SAVEFOLDER-":
            check_booleans(window, logo_file_ok, bck_dir_ok, save_dir_ok, x_ok, y_ok, s_ok)        

    window.close()

# Checks if all values are Ok to start program
def check_booleans(w, a, b, c, d, e, f):
    if a and b and c and d and e and f:
        w["-REFRESH-"].update(disabled=False)
        w["-START-"].update(disabled=False)
        w["-<-"].update(disabled=False)
        w["->-"].update(disabled=False)
    else:
        w["-REFRESH-"].update(disabled=True)
        w["-START-"].update(disabled=True)
        w["-<-"].update(disabled=True)
        w["->-"].update(disabled=True)

# Input: Background image dir.
def find_and_verify_images(b):

    # Variable setup
    comp_ext = [".jpg", ".jpeg", ".png"]
    bckgr_imgs = os.listdir(b)
   
    # Checks each file in dir if compatible formats and deletes if its not
    for i in reversed(range(len(bckgr_imgs))):
        for j in range(len(comp_ext)):
            if os.path.splitext(bckgr_imgs[i])[1].lower() == comp_ext[j]:
                break
            elif j == len(comp_ext) - 1:
                print(f"({bckgr_imgs[i]}) is not compatible and will not get processed")
                del bckgr_imgs[i]

        return bckgr_imgs

# Input: Width offset, Height offset, Background image, Logo image, Anchor point
def make_logo_location(ow, oh, b, l, a):
    ow = float(ow)
    oh = float(oh)
    bwidth, bheight = b.size
    lwidth, lheight = l.size
    ow = (ow * 0.01) * bwidth
    oh = (oh * 0.01) * bheight

    # Calculate logo position based on anchor and offsets
    if a == "Top Left":
        width = 0 + ow
        height = 0 + oh
    elif a == "Top Center":
        width = ((bwidth * 0.5) - (lwidth * 0.5)) + ow
        height = 0 + (oh * bheight)
    elif a == "Top Right":
        width = (bwidth - lwidth) - ow
        height = 0 + ow
    elif a == "Center Left":
        width = 0 + ow
        height = ((bheight * 0.5) - (lheight * 0.5)) + oh
    elif a == "Center":
        width = ((bwidth * 0.5) - (lwidth * 0.5)) + ow
        height = ((bheight * 0.5) - (lheight * 0.5)) + oh
    elif a == "Center Right":
        width = (bwidth - lwidth) - ow
        height = ((bheight * 0.5) - (lheight * 0.5)) + oh
    elif a == "Bottom Left":
        width = 0 + ow
        height = (bheight - lheight) - oh
    elif a == "Bottom Center":
        width = ((bwidth * 0.5) - (lwidth * 0.5)) + ow
        height = (bheight - lheight) - oh
    elif a == "Bottom Right":
        width = (bwidth - lwidth) - ow
        height = (bheight - lheight) - oh
    else:
        print("Error: no anchor point found")
        exit(1)

    return (round(width), round(height))

# Inputs: Background image, Logo image, Scale, Relative Scale
def logo_relative_size(b, l, s, rs):
    bwidth, bheight = b.size
    lwidth, lheight = l.size
    s = float(s)

    if rs == "Height" or (rs == "Smallest" and bwidth >= bheight):
        factor = float(lwidth / lheight)
        lheight = float(bheight * s)
        lwidth = float(lheight * factor)
    elif rs == "Width" or (rs == "Smallest" and bwidth <= bheight):
        factor = float(lheight / lwidth)
        lwidth = float(bwidth * s)
        lheight = float(lwidth * factor)
    else:
        print("ERROR: No scaling options fit condition")

    return (round(lwidth), round(lheight))

if __name__ == "__main__":
    main()