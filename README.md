# How to use the 3D Streeview Dashboard
This is a short 'how to' tutorial on using the 3D Streetview Dashboard being developed by [Rainbow Sensing 🌈📡](https://rainbowsensing.com/)

## Overview
The dashboard empowers users to create 3D meshes using nothing more than a camera phone. The true power of this approach should not be understated—like open-source platforms such as Wikipedia or OpenStreetMap, by unlocking this process to the +6 billion smartphone users in the world, the 3D Streetview Dashboard allows anyone, anywhere, to reconstruct their world in three dimensions. 

There are numerous use-cases for how this technology might be used for social good (anything that needs a high level of visual data, i.e., assessments of roads, building construction, solid waste management, or even post disaster needs). Fundamentally, being able to create a map in 3 dimensions allows for an unprecedented level of understanding of an area. These environments can be explored from a computer screen or in virtual reality. 

In that sense, the 3D Streetview Dashboard is one tool by which individuals can democratize the metaverse, by actively building it together, instead of waiting for multinational technology conglomerates with dubious intentions to do so for us 😒♾

--- 

## Tutorial
There are four main parts: server configuration, mesh project setup, imagery capture, and processing. After that, you will have a 3D mesh!

### Part One – Server Configuration 
Before even setting up your servers, you may want to simply go to the dashboard and create an account.

1. Go to https://3dstreetview.org/dashboard/ 

2. Sign in or get an account if you do not have one already by clicking ‘Guest’ in the top right corner and then register for an account.

After getting an account, the next thing you want to do is configure your server. You will need two servers to make this work. For now we are relying on [ODK Central](https://github.com/getodk/central) and our own privately hosted server. ODK is receiving images from the mobile phones, whereas the other server is [OpenDroneMap (ODM)](https://www.opendronemap.org/), where the processing is being done. **Note:** There is the option to also upload images directly, say from a drone or a camera, if that is your preference. 

3.	Once you are logged in, you will see the server option on the left panel. First set up the ODK server.  You will simply need to enter a name for the server, a URL, port, and then your username and password. For the ODM server it is the same, you just need to change your information for URL, port, username, and password. After you set up you will get the message 'Record was successfully created.'
  
### Part Two – Mesh Project Setup

Now that you’ve got your servers connected, you’ll need to set up the actual project itself. 
First, identify what you want to capture. As an example, let's say you want to create a 3D mesh of [The Lawn](https://en.wikipedia.org/wiki/The_Lawn), historic center of the University of Virginia, in Charlottesville.

![lawn_aerial_overhead_fall_ss_01](https://user-images.githubusercontent.com/36959983/143770486-180c75f9-da02-4d96-8d15-8b51e5af534f.jpg)

Here is an aerial image showing the area of interest—note the large building at the far right known as the Rotunda, this is the area we will focus on. To capture this, **or any other environment**, continue following these steps. 

4. On the left panel of the dashboard you should see an option called ‘Mesh projects’, click this

5. To create a new mesh, select the ‘create’ tab and proceed to fill out the necessary information.

If you do not have the coordinates ready, you can go on Google Maps or OpenStreetMap to get them. For example, go to the exact location you want on Google Maps and then simply left click, you should then have the latitude and longitude appear at the pin you created.

Or, if you prefer a more open-source method, simply go to [OpenStreetMap](https://osm.org/), zoom to the exact spot you want to collect your coordinates, right click and press 'show address' - it will appear on the screen for you to record.

 
![OSM Address 2](https://user-images.githubusercontent.com/36959983/143770876-d0bafd05-3f12-407a-9dab-a1817cbb5499.png)

Now fill in all the necessary info:
- Latitude: 38.03536
- Longitude: -78.50355
- Mesh name: The Lawn Test

Since you have already set up your servers, simply select the drop-down arrow and select the ones you are using. Finally, press ```New project``` and type in whatever name you want (you might as well stay consistent and keep the same name for both servers).

![Dasboard_Lawn Test](https://user-images.githubusercontent.com/36959983/143778121-1fa2c108-da05-417d-8e94-6ee0897e1bbf.png)

Your screen should look like the above. And that’s it! Now just hit save and you will be taken back to the mesh project page and see that ‘Record was successfully created’. Note that the web map now shows the location of your project. 

6.	The last step before being able to go collect data is to get your form. To do this, you’ll need to make sure you have added an ‘App User’ in the ODK Collect Server itself. So head over there, find the App Users tab to the right of Project Roles, and then click the blue button off to the write that says ```Create App User```. Enter any name, for example, ‘surveyor’. Now you should get a pop-up that says ```Success!``` and gives you a QR code. Note: Be sure under ```Form Access``` you have checked the box for your new user. 

7.	Switch back over to the 3D Streetview Dashboard and now click the 👁 icon to the far left of your project when you are still on the Mesh projects page. This will give you a QR code that you can scan in the ODK Collect mobile app, and it should automatically load the form on your phone. To ensure this has happened, just go to ```Fill Blank Form``` and you should see two empty forms, 3DStreetView_fill and 3DStreetView_main. You can also take a screenshot and send this QR code to any other surveyors, so they can quickly download the ODK form on their phones

Congratulations, your project is set up 🥳! Now you are ready for the hard part—going to the site and collecting tons of photos!

### Part Three – Imagery Capture
8.	Follow the steps of the form!

### Part Four – Processing
9.	Back to the dashboard, press some buttons. 

#### Below is an example of a (low-res) recent output from [Mohammad Maisha](https://github.com/maisha26) in Stone Town, Zanzibar ⬇
[Old Fort 3D](https://user-images.githubusercontent.com/36959983/143775448-4020138e-62c3-4520-bbcc-b9da5b38e3cf.mp4)
