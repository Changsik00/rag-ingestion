import json


# This is a manual check to see how metadata is retrieved
def test_metadata_extraction():
    # Let's simulate what _map_node_to_job does
    node_custom_metadata = '{"force_refresh": false}'
    custom_metadata = json.loads(node_custom_metadata)

    is_forced = custom_metadata.get("force_refresh") is True
    print(f"Is forced (is True check): {is_forced}")

    is_forced_simple = custom_metadata.get("force_refresh")
    print(f"Is forced (simple truthy check): {is_forced_simple}")

    # Check if a string 'false' would fail
    node_custom_metadata_str = '{"force_refresh": "false"}'
    custom_metadata_str = json.loads(node_custom_metadata_str)
    is_forced_str = custom_metadata_str.get("force_refresh") is True
    print(f"Is forced with string 'false' (is True check): {is_forced_str}")


if __name__ == "__main__":
    test_metadata_extraction()
