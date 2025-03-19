while read -r url; do
    wget -P local_libs "$url"
done < dependencies.txt