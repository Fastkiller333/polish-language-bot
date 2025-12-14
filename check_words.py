#!/usr/bin/env python3
"""
Utility script to check and preview words database
"""

import json
from collections import Counter

def main():
    print("🇵🇱 Loading words database...\n")
    
    with open('words_database.json', 'r', encoding='utf-8') as f:
        words = json.load(f)
    
    print(f"✅ Total words: {len(words)}\n")
    
    # Check for duplicates
    word_texts = [w['word'] for w in words]
    duplicates = [word for word, count in Counter(word_texts).items() if count > 1]
    
    if duplicates:
        print(f"⚠️  Found duplicate words: {duplicates}\n")
    else:
        print("✅ No duplicate words found\n")
    
    # Check ID sequence
    ids = [w['id'] for w in words]
    if ids != list(range(len(words))):
        print("⚠️  IDs are not sequential!\n")
    else:
        print("✅ IDs are sequential (0-299)\n")
    
    # Show first 5 words
    print("📚 First 5 words:\n")
    for i in range(min(5, len(words))):
        word = words[i]
        print(f"{word['id']}. {word['word']} - {word['translation']}")
    
    print("\n📚 Last 5 words:\n")
    for i in range(max(0, len(words)-5), len(words)):
        word = words[i]
        print(f"{word['id']}. {word['word']} - {word['translation']}")
    
    # Statistics
    print("\n📊 Statistics:\n")
    
    # Count words with full descriptions
    full_descriptions = sum(1 for w in words if len(w.get('description', '')) > 100)
    print(f"Words with full descriptions (>100 chars): {full_descriptions}")
    
    # Count words with examples
    with_examples = sum(1 for w in words if w.get('examples'))
    print(f"Words with examples: {with_examples}")
    
    # Count words with fun facts
    with_facts = sum(1 for w in words if w.get('fun_fact'))
    print(f"Words with fun facts: {with_facts}")
    
    # Show random word
    print("\n🎲 Random word preview:\n")
    import random
    random_word = random.choice(words)
    
    print(f"🇵🇱 Word: {random_word['word']}")
    print(f"Translation: {random_word['translation']}")
    print(f"Description: {random_word.get('description', 'N/A')[:100]}...")
    if random_word.get('examples'):
        print(f"Example: {random_word['examples'][0]}")
    if random_word.get('fun_fact'):
        print(f"Fun fact: {random_word['fun_fact'][:100]}...")
    
    print("\n✅ Database check complete!")

if __name__ == "__main__":
    main()




