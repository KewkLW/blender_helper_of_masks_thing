# Blender Random Duplicate Objects Addon

## Overview

A tool for creating mask animations for ComfyUI/ IPAdapter / Animatediff. The basics of the use case is to set your colors, move things around add key frames move them back add keyframes etc. Lots of randoms to get weird results. 

## Features

### 1. Random Duplication

Create multiple copies of an object with random variations:
- Choose how many duplicates to create
- Set the range for random positioning on X, Y, and Z axes
- Define minimum and maximum scaling for size variation
- Automatically group duplicates in a new collection for easy management

### 2. Randomize Location

Quickly shuffle the positions of selected objects:
- Specify a range for random movement
- Apply to multiple objects at once for instant scene variation

### 3. Split Faces

Transform a single object into multiple separate pieces:
- Split connected faces into individual objects
- Automatically set the origin point to the center of each new object
- Record the original location of each piece for easy reassembly

### 4. Move to Origin

Return split or moved objects to their original positions:
- Instantly move selected objects back to where they were created
- Useful for resetting a scene or undoing complex movements

### 5. Set Origin

Update the recorded origin point for objects:
- Set the current location as the new "home" position for an object
- Affects where the object will return to when using "Move to Origin"

### 6. Material Assignment

Quickly add colorful materials to your objects:
- Choose from a preset list of vibrant colors
- Add emission to materials for a glowing effect
- Apply random colors to multiple objects at once

## How to Use

1. **Random Duplication**: Select an object, set your desired parameters, and click "Random Duplicate" to create variations.

2. **Randomize Location**: Select objects you want to reposition, set the location range, and click "Randomize Location" to shuffle their positions.

3. **Split Faces**: Select a complex object and click "Split Faces" to break it into its component parts. Each part will remember where it came from.

4. **Move to Origin**: After moving split pieces or any objects, select them and click "Move to Origin" to return them to their original positions.

5. **Set Origin**: If you've moved objects and want their new positions to be considered the "original" position, select them and click "Set Origin".

6. **Add Materials**: Select objects and either choose a specific color or click "Random Color" to quickly assign eye-catching materials.

## Installation

1. Download the `.py` file from this repository.
2. Open Blender and go to Edit > Preferences > Add-ons.
3. Click "Install" and select the downloaded file.
4. Enable the addon by checking the box next to its name.

## Compatibility

This has only been tested with 4.3 but should be good down to 3.3. 

## Support and Contributions

If you encounter any issues or have suggestions for improvements, please open an issue on this GitHub repository. Contributions via pull requests are welcome!
