set vers=%*
echo Ready to generate update for %vers%
pause
pyupdater build tcode_generator.py --console --app-version %vers%
pyupdater pkg --process --sign
pyupdater upload -s s3
echo Done uploading update!