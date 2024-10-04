@echo off
setlocal


set "profile_url=https://www.roblox.com/users/THEIR_ID/profile"


set "output_file=user_profile.html"


curl -o "%output_file%" "%profile_url%"


findstr /C:"<div class=\"btr-header-status-text" "%output_file%" > user_profile_status.log


endlocal
