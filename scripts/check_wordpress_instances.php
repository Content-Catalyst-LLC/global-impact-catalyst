<?php
// Minimal WordPress stubs for release rendering checks.
define('ABSPATH', __DIR__ . '/');
function plugin_dir_url($file) { return 'https://example.test/plugin/'; }
function wp_register_style() {}
function wp_register_script() {}
function add_action() {}
function register_activation_hook() {}
function wp_enqueue_style() {}
function wp_enqueue_script() {}
function wp_localize_script() {}
function add_shortcode() {}
function esc_attr($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
function esc_url($value) { return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8'); }
function esc_url_raw($value) { return $value; }
function wp_rand($min, $max) { static $counter = 1000; return $counter++; }
function is_user_logged_in() { return true; }
function current_user_can($capability) { return true; }
function rest_url($path='') { return 'https://example.test/wp-json/' . ltrim($path, '/'); }
function wp_create_nonce($action) { return 'test-nonce'; }
require __DIR__ . '/../wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php';
$html = gic_demo_shortcode() . gic_demo_shortcode();
preg_match_all('/\sid="([^"]+)"/', $html, $matches);
$ids = $matches[1];
if (count($ids) !== count(array_unique($ids))) { fwrite(STDERR, "Duplicate shortcode IDs detected.\n"); exit(1); }
preg_match_all('/\sfor="([^"]+)"/', $html, $label_matches);
foreach ($label_matches[1] as $target) {
    if (!in_array($target, $ids, true)) { fwrite(STDERR, "Label target is missing: {$target}\n"); exit(1); }
}
if (substr_count($html, 'data-gic-demo') !== 2) { fwrite(STDERR, "Expected two demo instances.\n"); exit(1); }
foreach (array('name="workspace"','name="indicatorDefinition"','name="designType"','name="claimType"') as $needle) {
    if (substr_count($html, $needle) !== 2) { fwrite(STDERR, "Canonical field missing: {$needle}\n"); exit(1); }
}
$workspace = gic_workspace_shortcode();
foreach (array('data-gic-workspace','data-gic-workspace-list','data-gic-workspace-save','data-gic-workspace-import') as $needle) {
    if (strpos($workspace, $needle) === false) { fwrite(STDERR, "Workspace control missing: {$needle}\n"); exit(1); }
}
if (substr_count($workspace, 'data-gic-demo') !== 1) { fwrite(STDERR, "Workspace must preserve one canonical editor.\n"); exit(1); }
$evidence = gic_evidence_ledger_shortcode();
foreach (array('data-gic-evidence-ledger','data-gic-source-form','data-gic-evidence-form','data-gic-dataset-form','data-gic-claim-link-form','data-gic-evidence-load') as $needle) {
    if (strpos($evidence, $needle) === false) { fwrite(STDERR, "Evidence ledger control missing: {$needle}\n"); exit(1); }
}
preg_match_all('/\sid="([^"]+)"/', $evidence, $evidence_ids);
preg_match_all('/\sfor="([^"]+)"/', $evidence, $evidence_labels);
foreach ($evidence_labels[1] as $target) {
    if (!in_array($target, $evidence_ids[1], true)) { fwrite(STDERR, "Evidence label target is missing: {$target}\n"); exit(1); }
}
$registry = gic_indicator_registry_shortcode();
foreach (array('data-gic-indicator-registry','data-gic-registry-workspace','data-gic-registry-load','data-gic-unit-form','data-gic-indicator-form','data-gic-baseline-form','data-gic-target-form','data-gic-method-form') as $needle) {
    if (strpos($registry, $needle) === false) { fwrite(STDERR, "Indicator registry control missing: {$needle}\n"); exit(1); }
}
preg_match_all('/\sid="([^"]+)"/', $registry, $registry_ids);
preg_match_all('/\sfor="([^"]+)"/', $registry, $registry_labels);
foreach ($registry_labels[1] as $target) {
    if (!in_array($target, $registry_ids[1], true)) { fwrite(STDERR, "Registry label target is missing: {$target}\n"); exit(1); }
}

$measurement = gic_measurement_portfolio_shortcode();
foreach (array('data-gic-measurement-portfolio','data-gic-observation-form','data-gic-beneficiary-form','data-gic-beneficiary-observation-form','data-gic-financial-form','data-gic-outcome-portfolio-form','data-gic-outcome-member-form','data-gic-outcome-aggregate-form') as $needle) {
    if (strpos($measurement, $needle) === false) { fwrite(STDERR, "Measurement control missing: {$needle}\n"); exit(1); }
}
preg_match_all('/\sid="([^"]+)"/', $measurement, $measurement_ids);
preg_match_all('/\sfor="([^"]+)"/', $measurement, $measurement_labels);
foreach ($measurement_labels[1] as $target) {
    if (!in_array($target, $measurement_ids[1], true)) { fwrite(STDERR, "Measurement label target is missing: {$target}\n"); exit(1); }
}

$review = gic_review_workflow_shortcode();
foreach (array('data-gic-review','data-gic-review-load','data-gic-review-assignment','data-gic-review-assessment','data-gic-review-list') as $needle) {
    if (strpos($review, $needle) === false) { fwrite(STDERR, "Review workflow control missing: {$needle}\n"); exit(1); }
}
preg_match_all('/\sid="([^"]+)"/', $review, $review_ids);
preg_match_all('/\sfor="([^"]+)"/', $review, $review_labels);
foreach ($review_labels[1] as $target) {
    if (!in_array($target, $review_ids[1], true)) { fwrite(STDERR, "Review label target is missing: {$target}\n"); exit(1); }
}

$analysis = gic_analysis_studio_shortcode();
foreach (array('data-gic-analysis-studio','data-gic-analysis-load','data-gic-analysis-trend','data-gic-analysis-benchmark','data-gic-analysis-uncertainty','data-gic-analysis-scenario','data-gic-analysis-results') as $needle) {
    if (strpos($analysis, $needle) === false) { fwrite(STDERR, "Analysis Studio control missing: {$needle}\n"); exit(1); }
}
echo "WordPress v1.7.0 workspace, evidence ledger, indicator registry, measurement portfolio, review workflow, analysis studio, and multi-instance contract passed for " . count($ids) . " unique demo IDs.\n";
