#!/usr/bin/env python3
"""
Mini Research Assistant (DuckDuckGo version)
---------------------------------------------
This Mini research assistant uses free API key from Duckduckgo for instant answers.

I have used DuckDuckGo's Instant Answer API to provide quick factual answers to user queries.
The assistant takes a search query as input and returns a simplified result including the heading, abstract, source, URL, and related topics.
This works good for factual questions, e.g., "What is photosynthesis?" but may not be affective for things like "Best restaurants near me".
"""

import sys
import requests
import google.generativeai as genai
import os
from colorama import Fore, Style

DUCKDUCKGO_API_URL = "https://api.duckduckgo.com/"


def duckduckgo_search(query: str):
    """Query DuckDuckGo's Instant Answer API and return a simplified result."""
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }

    response = requests.get(DUCKDUCKGO_API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    result = {
        "heading": data.get("Heading"),
        "abstract": data.get("AbstractText"),
        "source": data.get("AbstractSource"),
        "url": data.get("AbstractURL"),
        "related_topics": [],
    }

    for topic in data.get("RelatedTopics", [])[:5]:
        if isinstance(topic, dict) and topic.get("Text"):
            result["related_topics"].append(
                {
                    "text": topic.get("Text"),
                    "url": topic.get("FirstURL"),
                }
            )

    return result


def print_result(result):
    if result["abstract"]:
        print(Fore.YELLOW + f"\n{result['heading']}" + Style.RESET_ALL)
        print(Fore.LIGHTGREEN_EX + f"{result['abstract']}" + Style.RESET_ALL)
        if result["source"]:
            print(Fore.GREEN+ f"(Source: {result['source']})"+Style.RESET_ALL)
        if result["url"]:
            print(Fore.GREEN +f"More: {result['url']}"+ Style.RESET_ALL)
    else:
        print("\nNo direct answer found.")

    if result["related_topics"]:
        print(Fore.MAGENTA+"\nRelated:"+Style.RESET_ALL)
        for i, topic in enumerate(result["related_topics"], 1):
            print(Fore.CYAN + f"{i}. {topic['text']}" +Style.RESET_ALL)
            if topic["url"]:
                print(Fore.CYAN+ f"   {topic['url']}"+ Style.RESET_ALL)

def summarize_with_gemini(result):
    """We are sending query to Gemini and get a natural-language summary."""
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-3.5-flash-lite")

    prompt = f"Summarize this in a friendly, conversational way:\n\n{result['heading']}\n{result['abstract']}"

    response = model.generate_content(prompt)
    return response.text

def main():
    if len(sys.argv) < 2:
        print(Fore.MAGENTA+'Usage: python search_assistant.py "your search query"'+Style.RESET_ALL)
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"Searching for: {query}")

    try:
        result = duckduckgo_search(query)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print_result(result)
    
    print("\nGetting AI summary by Gemini....")
    google_summary= summarize_with_gemini(result)
    print("\n--- Gemini AI summary ---")
    print(google_summary)


if __name__ == "__main__":
    main()
