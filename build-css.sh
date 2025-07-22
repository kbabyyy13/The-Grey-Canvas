
#!/bin/bash

echo "Building optimized CSS..."

# Create output directory if it doesn't exist
mkdir -p static/css

# Build Tailwind CSS
npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.min.css --minify

# Process with PostCSS for additional optimizations
npx postcss ./static/css/tailwind.min.css -o ./static/css/optimized.css

echo "CSS build complete! Optimized file: static/css/optimized.css"

# Show file size comparison
echo "File sizes:"
if [ -f "static/css/tailwind.min.css" ]; then
  echo "Minified: $(wc -c < static/css/tailwind.min.css) bytes"
fi
if [ -f "static/css/optimized.css" ]; then
  echo "Optimized: $(wc -c < static/css/optimized.css) bytes"
fi
