## Design theme for app
- Navigate to https://new.express.adobe.com/your-stuff/files to use Adobe Express interface
- Duplicate an existing image, alter text and tick colour and make background colour to transparent
- Download as "Transparent PNG"
- Now set the Background colour to the BACKGROUND_COLOUR hex setting you want to use for the app. Make sure you also set this value in your app's settings.py

## Format banner.png and ticked.png
- Open PNG image in GIMP
- Click Image > "Crop to Content"
- Now File > "Export As..." and navigate to the static/images/ directory for the app. Save as "banner.png"
- Use the crop tool to crop just the tick logo, and repeat the "Crop to Content" step.
- Export as static/images/ticked.png

## Create favicon.ico
- Now navigate to https://favicon.io/favicon-converter/ and drag and drop the ticked.png you just created, and click Download
- Unzip the favicon_io.zip file in your Downloads folder. Copy the favicon.ico file to the app's static/images/
