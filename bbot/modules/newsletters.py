# Created a new module called 'newsletters' that will scrape the websites (or recursive websites,
# thanks to BBOT's sub-domain enumeration) looking for the presence of an 'email type' that also
# contains a 'placeholder'. The combination of these two HTML items usually signify the presence
# of an "Enter Your Email Here" type Newsletter Subscription service. This module could be used
# to find newsletters for a future email bombing attack and/or find user-input fields that could
# be be susceptible to overflows or injections.

from .base import BaseModule
import re
from bs4 import BeautifulSoup

# Known Websites with Newsletters
# https://futureparty.com/
# https://www.marketingbrew.com/
# https://buffer.com/
# https://www.milkkarten.net/
# https://geekout.mattnavarra.com/

deps_pip = ["beautifulsoup4"]


class newsletters(BaseModule):
    watched_events = ["HTTP_RESPONSE"]
    produced_events = ["FINDING"]
    flags = ["passive", "safe"]
    meta = {"description": "Searches for Newsletter Submission Entry Fields on Websites"}

    # Parse through Website to find a Text Entry Box of 'type = email'
    # and ensure that there is placeholder text within it.
    def find_type(self, soup):
        email_type = soup.find(type="email")
        if email_type:
            regex = re.compile(r"placeholder")
            if regex.search(str(email_type)):
                return True
        return False

    async def handle_event(self, event):
        if event.data["status_code"] == 200:
            soup = BeautifulSoup(event.data["body"], "html.parser")
            result = self.find_type(soup)
            if result:
                newsletter_result = self.make_event(
                    data=event.data["url"], 
                    event_type="NEWSLETTER", 
                    source=event, 
                    tags=event.tags
                )
                # self.emit_event(newsletter_result)
                description = f"Found a Newsletter Submission Form that could be used for email bombing attacks"
                data = {"host": str(event.host), "description": description, "url":event.data["url"]}

                self.emit_event(data, "FINDING", event)
