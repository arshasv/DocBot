#!/bin/bash

set -e

generate_pin_order_file() {
    local north_pins=$1
    local south_pins=$2
    local east_pins=$3
    local west_pins=$4
    local design_name=$5
    local output_base_dir=${6:-"./designs"}

    local design_dir="$output_base_dir/$design_name"
    mkdir -p "$design_dir"

    local pin_order_file="$design_dir/pin_order.cfg"
    {
        echo "#N"
        echo "@min_distance=0.1"
        echo "$north_pins" | tr ',' '\n'
        echo "#S"
        echo "$south_pins" | tr ',' '\n'
        echo "#E"
        echo "$east_pins" | tr ',' '\n'
        echo "#W"
        echo "$west_pins" | tr ',' '\n'
    } > "$pin_order_file"

    echo "$pin_order_file"
}

# Function to generate config.tcl and .sdc
generate_openroad_files() {
    local design_name=$1
    local clock_period=$2
    local clock_port=$3
    local north_pins=$4
    local south_pins=$5
    local east_pins=$6
    local west_pins=$7
    local output_base_dir=${8:-"./designs"}
    local die_area=$9

    local design_dir="$output_base_dir/$design_name"
    local src_dir="$design_dir/src"
    mkdir -p "$src_dir"

    local config_file="$design_dir/config.tcl"
    local sdc_file="$src_dir/${design_name}.sdc"

    generate_pin_order_file "$north_pins" "$south_pins" "$east_pins" "$west_pins" "$design_name" "$output_base_dir"

    {
        echo "set_units -time ns"
        echo "create_clock [get_ports $clock_port] -name core_clock -period $clock_period"
    } > "$sdc_file"

    {
        echo "##################################################################"
        echo "# GENERAL"
        echo "##################################################################"
        echo "set ::env(DESIGN_NAME) \"$design_name\""
        echo "set ::env(PDK) \"sky130B\""
        echo "set ::env(VERILOG_FILES) [glob \$::env(DESIGN_DIR)/src/*.v]"
        echo "set ::env(CLOCK_PERIOD) $clock_period"
        echo "set ::env(CLOCK_PORT) \"$clock_port\""
        echo "set ::env(CLOCK_NET) \"$clock_port\""
        echo "##################################################################"
        echo "# FLOORPLAN"
        echo "##################################################################"
        if [[ -n "$die_area" ]]; then
            echo "set ::env(FP_SIZING) \"absolute\""
            echo "set ::env(DIE_AREA) \"$die_area\""
        else
            echo "set ::env(FP_SIZING) \"relative\""
        fi
        echo "set ::env(FP_PIN_ORDER_CFG) [glob \$::env(DESIGN_DIR)/pin_order.cfg]"
    } > "$config_file"

    echo "Generated configuration files for $design_name"
}

# Ensure OpenLane2 repo
if [ ! -d "openlane2" ]; then
    git clone https://github.com/efabless/openlane2.git || { echo "Failed to clone OpenLane2"; exit 1; }
fi
cd openlane2 || { echo "Cannot access OpenLane2 directory"; exit 1; }

mkdir -p designs

# Read inputs
if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <design_name> <clock_period> <clock_port> [north_pins] [south_pins] [east_pins] [west_pins] [die_area]"
    exit 1
fi

design_name=$1
clock_period=$2
clock_port=$3
north_pins=${4:-""}
south_pins=${5:-""}
east_pins=${6:-""}
west_pins=${7:-""}
die_area=${8:-""}

# Copy Verilog file from local path
local_verilog_path="/home/dell/Desktop/Arsha/DocBot/alu.v"  # Adjust this path if needed
design_src_dir="designs/$design_name/src"
mkdir -p "$design_src_dir"
cp "$local_verilog_path" "$design_src_dir/" || { echo "Failed to copy local Verilog file"; exit 1; }

# Save design name
echo "$design_name" > designs/info.txt
chmod -R 777 "designs/$design_name"
chown -R $(whoami):$(whoami) "designs/$design_name"

# Generate configuration files
generate_openroad_files "$design_name" "$clock_period" "$clock_port" "$north_pins" "$south_pins" "$east_pins" "$west_pins" "./designs" "$die_area"
