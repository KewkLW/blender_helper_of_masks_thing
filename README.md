Got it! Let's update the README to include the missing features and provide a comprehensive guide.

---

# Random Duplicate Objects with Extended Features

## Overview

Hi!!! I'm Chat G... P... T... your friendly digital guide on this ComfyUI Mask Helper Creator... um thingy tour. This shnazzy Blender addon is your new best friend for enhancing your masking adventures. With this tool, you can create random duplicates of objects, split faces, manage materials with some fancy shmancy emission properties, adjust object origins, and tinker with various render settings. Oh, and did I mention it has some nifty tools for managing keyframes in your animations? Buckle up; it's going to be a fun ride!

## Features

### Random Duplicate Objects
- **Create Random Duplicates**: Generates multiple duplicates with random locations. 
    - For the most part you probably want to keep y at 0.  
- **Randomize Location**: Adjust the positions of your selected objects within a specified range.
- **Split Faces**: Add new geometry by splitting the faces of selected objects.
    - I use this to create a plan, subdivide it, then split it. When it splits it records the location of each individual new object. This is helpful because you can then move things around and create keyframes then easy come back to where you were and create keyframes. 
- **Move to Origin**: Quickly move selected objects to their original recorded locations.
- **Set New Origin**: Define a new origin for selected objects at their current location. 
    - You don't have to use this after split frames as it already does it.

### Material Management
- **Add Material with Emission**: Apply RGB CMYK W materials with emission properties to your objects. This works singular and with multiple objects selected.
- **Add Random Material with Emission**: Give your objects a randomly selected emission material from RGB CMYK W.
    - This is also useful for cubes. You can split faces, random color, and then do some fun transitions with the various side of the cube. Just animate it as 1. Could assign an empty to it first and animate that instead. I may add this as functionality later. 

### Render Settings
- **Set Render Resolution**: Set your render dims to 512 or 1024 as masks are 1:1 atm.
- **Fix Color**: Adjust the color view transform to 'Standard' to ensure the correct RGB CMYK W values are picked up by the renderer.

### Keyframe Management
- **Remove Past Keyframes**: Delete all keyframes before the current frame for selected objects.
- **Remove Future Keyframes**: Delete all keyframes after the current frame for selected objects.
    - *I use this to easily remove frames after duplicating objects. I'll first create my complete animation using 1 object, then I go back and figure out where I want transitions and duplicate the object then remove the past frames of the new object and the future frames of the old object so they don't over lap. Then assign it a color. 

### Additional Utilities
- **Random Resize**: Randomly resize selected objects within a specified scale range.
    - This is useful for speheres instead of planes.

## Installation

1. Download the addon as a random_object_duplicate_plus.py file.
2. In Blender, navigate to `Edit > Preferences > Add-ons`.
3. Click `Install...` and select the downloaded random_object_duplicate_plus.py
4. Enable the addon by checking the box next to "Random Duplicate Objects with Extended Features".

This will show up in your sidebar as Kewky ComfyUI Tools.

## Usage

### Accessing the Addon
Find all the features of the addon in the `View3D` tool shelf under the `Kewky ComfyUI Tools` tab.

### Random Duplicate Objects

1. **Create Random Duplicates**
    - Set the number of duplicates and specify transformation ranges.
    - Click `Random Duplicate`.

2. **Randomize Location**
    - Define the location range.
    - Click `Randomize Location`.

3. **Split Faces**
    - Select the objects.
    - Click `Split Faces`.

4. **Move to Origin**
    - Select the objects.
    - Click `Move to Origin`.

5. **Set New Origin**
    - Select the objects.
    - Click `Set New Origin`.

### Material Management

1. **Add Material with Emission**
    - Select your objects.
    - Choose a color and name for the material.
    - Click `Add Material with Emission`.

2. **Add Random Material with Emission**
    - Select your objects.
    - Click `Random Color`.

### Render Settings

1. **Set Render Resolution**
    - Choose a resolution (512x512 or 1024x1024).
    - Click the respective button.

2. **Fix Color**
    - Click `Fix Color` to set the view transform to 'Standard'.

### Keyframe Management

1. **Remove Past Keyframes**
    - Select the object with keyframes.
    - Click `Remove Past`.

2. **Remove Future Keyframes**
    - Select the object with keyframes.
    - Click `Remove Future`.

### Additional Utilities

1. **Random Resize**
    - Define the minimum and maximum scale values.
    - Select the objects.
    - Click `Random Resize`.

## Properties

### Random Duplicate Properties
- `num_duplicates`: Number of duplicates to create.
- `x_range`: Range for random X-axis transformation.
- `y_range`: Range for random Y-axis transformation.
- `z_range`: Range for random Z-axis transformation.
- `scale_min`: Minimum scale for duplicates.
- `scale_max`: Maximum scale for duplicates.
- `group_name`: Group name for organizing duplicates.
- `loc_range`: Range for random location adjustment.

## Support

I tested this mostly on 4.3. Some on 4.2 and very little on 3.3 LTS. Basically just made sure it worked. I "think" there's nothing version specific in it so it should work far back as 2.8. Mind you, this does not mean if it doesn't that I'll make it work on any older version. :) But feel free to drop bugs and feature requests. 

