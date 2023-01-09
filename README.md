
This reads items (states) that are not currently in the file 'scraped.json'. 
- Make sure to check this file and remove states if you want to re-scrape it.

It will scrape the target website and output a csv file to './states/'.

To use script, make sure python is installed
- Python 3.6+

1. Clone the repository and navigate into the root of the folder

2. Create a virtual environment
`python3 -m venv venv`

3. Activate the virtual environment:
- Windows: `.\venv\Scripts\Activate`
- Mac/Linux: `source venv/bin/activate`

4. Install script dependencies
`pip install -r requirements.txt`

5. Run the script with arguments
`python scrape.py`
 - Or run an individual state: `python scrape.py --state "West Virginia"`


