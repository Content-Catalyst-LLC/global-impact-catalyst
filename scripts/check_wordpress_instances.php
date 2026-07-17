<?php
// Minimal WordPress stubs for release rendering checks.
define('ABSPATH', __DIR__);
function plugin_dir_url($file) { return 'https://example.test/plugin/'; }
function wp_register_style() {}
function wp_register_script() {}
function add_action() {}
function wp_enqueue_style() {}
function wp_enqueue_script() {}
function add_shortcode() {}
function esc_attr($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
function wp_rand($min, $max) { static $counter = 1000; return $counter++; }
require __DIR__ . '/../wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php';
$html = gic_demo_shortcode() . gic_demo_shortcode();
preg_match_all('/\sid="([^"]+)"/', $html, $matches);
$ids = $matches[1];
if (count($ids) !== count(array_unique($ids))) { fwrite(STDERR, "Duplicate shortcode IDs detected.\n"); exit(1); }
preg_match_all('/\sfor="([^"]+)"/', $html, $label_matches);
foreach ($label_matches[1] as $target) {
    if (!in_array($target, $ids, true)) { fwrite(STDERR, "Label target is missing: {$target}\n"); exit(1); }
}
if (substr_count($html, 'data-gic-demo') !== 2) { fwrite(STDERR, "Expected two shortcode instances.\n"); exit(1); }
foreach (array('name="workspace"','name="indicatorDefinition"','name="designType"','name="claimType"') as $needle) {
    if (substr_count($html, $needle) !== 2) { fwrite(STDERR, "Canonical field missing from one or more instances: {$needle}\n"); exit(1); }
}
echo "WordPress v1.1.0 multi-instance contract passed for " . count($ids) . " unique IDs.\n";
