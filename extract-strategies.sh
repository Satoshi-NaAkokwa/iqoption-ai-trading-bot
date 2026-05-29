#!/bin/bash
# Extract top 10 videos from Katie Tutorials channel and get transcripts

# Video IDs from the channel (top IQ Option relevant ones)
VIDEOS=(
  "crBn6kSAQWA"  # IQ Option Best 1 Minute Strategy
  "QHld3u6fAa4"  # My win using Moving Averages + RSI
  "DrQ3Ffv1kN4"  # Easiest Pocket Option Trading Strategy
  "5OjAv4NF288"  # Pocket Option Best Indicators Trading Strategy
  "pojqs15lHg8"  # My win method
  "x6W-kAo3SOI"  # Pocket Option quick trading strategy
  "-YASghts1KE"  # Testing My 2-Minute Strategy
  "uShRF-2-Ebc"  # My 19,720 Session: 2 Minute Method
  "JEV4h0IN83A"  # 56,450 Result Strategy Analysis
  "Sxh-P607TpI"  # 53,917 Trading Session: 2 Indicators
)

OUTPUT_DIR="/home/openclaw/.openclaw/workspace/strategy-analysis"
mkdir -p "$OUTPUT_DIR"

echo "Extracting video information and transcripts..."
echo ""

for VIDEO_ID in "${VIDEOS[@]}"; do
  echo "Processing: $VIDEO_ID"

  # Get video title
  TITLE=$(yt-dlp --get-title "https://www.youtube.com/watch?v=$VIDEO_ID" 2>/dev/null | head -1)
  echo "Title: $TITLE"

  # Get transcript (subtitles)
  yt-dlp --write-subs --write-auto-subs --sub-lang en --skip-download \
    --sub-format vtt --output "$OUTPUT_DIR/${VIDEO_ID}" \
    "https://www.youtube.com/watch?v=$VIDEO_ID" 2>/dev/null

  # Get video description
  yt-dlp --get-description "https://www.youtube.com/watch?v=$VIDEO_ID" 2>/dev/null > "$OUTPUT_DIR/${VIDEO_ID}_description.txt"

  echo "Saved to: $OUTPUT_DIR/${VIDEO_ID}"
  echo "---"
done

echo "Done! Files saved to $OUTPUT_DIR"