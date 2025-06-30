# Changelog
# [1.4.1]
Fixed:
- Schedule activation fix

Changed:
- Improved Dark Mode

# [1.4.0]
Added:
- Public Wiki
- Logs for auto-wake schedule activity
- Dark mode (crude)
- PWA support for Chrome, iOS and Android
- Indocator if schedule is enabled
- Added help texts in forms
- Added custom checkbox widget

Changed:
- Refactoring
- Bugfixes

# [1.3.0]
Added:
- Added search functionality
- Added statistic for server uptime
- Created an icon

Changed:
- Clarified docker compose instruction in README.md
- Improved mobile (phone) appearance
- Improved Homelab dropdown menu selectability on mobile
- Changed licensing terms: Prohibiting commeercial use
- Only show server buttons if action is available
- Improved display of schedules
- Refactoring

# [1.2.0]
Added:
- Server Time display in footer

Fixed:
- Bugfixes that occured after 1.1.0 release

Changed:
- Provided alternative in_online check: Added an endpoint that can be triggered by JS in the browser -> Reduced loading times

# [1.1.0]
Changed:
- Fix executing non-repeating schedules every day
- Fix not showing profile and logout information when a message is present
- Inline Buttons restyled

Added:
- Introduced Homelab and Wiki model
- Added Wiki / overview section on top of dashboard
- Added Homelab selection

# [1.0.0] - Starting to get useful
Added:
- Shutdown via POST request
- Timed (cron) functionality: Waking and shutting Server down based on a Schedule

Changed:
- Refactorings
- Various bug fixes

# [0.1.0] - Initial release
Some planned functionality, like cron waking and scheduling, is still missing but the overall project structure is now implemented.
