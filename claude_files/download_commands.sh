#!/bin/bash

# Quick Download Commands for Warren's Selected Books
# Just copy-paste these commands in your terminal

echo "=========================================="
echo "📚 Downloading Your Selected Books"
echo "=========================================="
echo ""
echo "Files will be saved to: ~/Desktop/AArchive/"
echo ""

# Book 1: Introduction to Game Design, Prototyping, and Development
echo "Book 1: Gibson Bond (Introduction to Game Design, Prototyping, and Development)"
echo "→ Recommend #6: 3rd Edition (2022)"
echo ""
search download "Introduction to Game Design Prototyping Development Jeremy Gibson Bond" --interactive

echo ""
echo ""

# Unity Book Options
echo "Book 2: Unity By Example - Choose one:"
echo ""
echo "Option A: Unity Development Cookbook (RECOMMENDED)"
echo "  → Most practical, recipe-based approach"
echo "  → #1: 2nd Edition (latest)"
search download "Unity Development Cookbook" --interactive

echo ""
echo "OR"
echo ""
echo "Option B: Unity By Example (2018)"
echo "  → Project-based learning"
search download "Unity 2018 By Example game development" --interactive

echo ""
echo ""

# Godot Book Options
echo "Book 3: Godot By Example - Choose one:"
echo ""
echo "Option A: Godot 4 Game Development Projects (RECOMMENDED)"
echo "  → Most recent (Godot 4)"
echo "  → 5 complete project tutorials"
echo "  → #3 or #6: 2nd Edition"
search download "Godot 4 Game Development Projects" --interactive

echo ""
echo "OR"
echo ""
echo "Option B: Godot 4 Game Development Cookbook"
echo "  → Recipe-based approach"
echo "  → 50+ recipes"
search download "Godot 4 Game Development Cookbook" --interactive

echo ""
echo "=========================================="
echo "✅ Done!"
echo "=========================================="
