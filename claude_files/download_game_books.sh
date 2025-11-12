#!/bin/bash

# Game Development Books Download Script
# Run this to download the recommended books interactively

echo "=========================================="
echo "Game Development Books Download"
echo "=========================================="
echo ""
echo "You have 25 downloads/day quota."
echo "Files will be saved to: ~/Desktop/AArchive/"
echo ""
echo "TIP: For each book, I recommend:"
echo "  1. Game Programming Patterns -> Select any (all good)"
echo "  2. Gibson Bond -> Select #6 (3rd Edition)"
echo "  3. Art of Game Design -> Select #1 or #4 (10th Anniversary or 2nd Edition)"
echo "  4. Theory of Fun -> Select #2 (2nd Edition)"
echo "  5. Advanced Game Design -> Select #1"
echo ""
echo "=========================================="
echo ""

# Book 1: Game Programming Patterns
echo "📚 [1/5] Game Programming Patterns by Robert Nystrom"
echo "     (Select any version - all are good)"
echo ""
search download "Game Programming Patterns Robert Nystrom" --interactive
echo ""

# Book 2: Gibson Bond
echo "📚 [2/5] Introduction to Game Design, Prototyping, and Development"
echo "     (Recommend #6: 3rd Edition for latest content)"
echo ""
search download "Introduction to Game Design Prototyping Development Jeremy Gibson Bond" --interactive
echo ""

# Book 3: Art of Game Design
echo "📚 [3/5] The Art of Game Design: A Book of Lenses"
echo "     (Recommend #1: 10th Anniversary Edition)"
echo ""
search download "Art of Game Design Book of Lenses Jesse Schell" --interactive
echo ""

# Book 4: Theory of Fun
echo "📚 [4/5] A Theory of Fun for Game Design"
echo "     (Recommend #2: 2nd Edition)"
echo ""
search download "Theory of Fun for Game Design Raph Koster" --interactive
echo ""

# Book 5: Advanced Game Design
echo "📚 [5/5] Advanced Game Design: A Systems Approach"
echo "     (Select #1)"
echo ""
search download "Advanced Game Design Systems Approach Michael Sellers" --interactive
echo ""

echo "=========================================="
echo "✅ Done! Check ~/Desktop/AArchive/ for your books"
echo "=========================================="
echo ""
echo "Recommended reading order:"
echo "  1. Theory of Fun (quick read, 2-3 days)"
echo "  2. Game Programming Patterns (1-2 weeks)"
echo "  3. Gibson Bond (hands-on, 2-4 weeks)"
echo "  4. Art of Game Design (ongoing reference)"
echo "  5. Advanced Game Design (when ready)"
echo ""
