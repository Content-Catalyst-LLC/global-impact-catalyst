<?php
/**
 * Plugin Name: Global Impact Catalyst
 * Description: Persistent impact workspaces, evidence chains, governed indicators, measurement, review, analysis, reporting, public APIs, governed embeds, Sustainable Catalyst handoffs, reproducible exports, and canonical contract demo. Shortcodes: [global_impact_catalyst_integration_hub], [global_impact_catalyst_reporting_studio], [global_impact_catalyst_analysis_studio], [global_impact_catalyst_review_workflow], [global_impact_catalyst_measurement_portfolio], [global_impact_catalyst_workspace], [global_impact_catalyst_evidence_ledger], [global_impact_catalyst_indicator_registry], [global_impact_catalyst_demo]
 * Version: 1.9.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('GIC_DEMO_VERSION', '1.9.0');
define('GIC_DEMO_URL', plugin_dir_url(__FILE__));

function gic_demo_register_assets() {
    wp_register_style('global-impact-catalyst-demo', GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.css', array(), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-demo', GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-workspace', GIC_DEMO_URL . 'assets/global-impact-catalyst-workspace.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-workspace', GIC_DEMO_URL . 'assets/global-impact-catalyst-workspace.js', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-evidence', GIC_DEMO_URL . 'assets/global-impact-catalyst-evidence.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-evidence', GIC_DEMO_URL . 'assets/global-impact-catalyst-evidence.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-registry', GIC_DEMO_URL . 'assets/global-impact-catalyst-registry.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-registry', GIC_DEMO_URL . 'assets/global-impact-catalyst-registry.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-measurement', GIC_DEMO_URL . 'assets/global-impact-catalyst-measurement.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-measurement', GIC_DEMO_URL . 'assets/global-impact-catalyst-measurement.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-review', GIC_DEMO_URL . 'assets/global-impact-catalyst-review.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-review', GIC_DEMO_URL . 'assets/global-impact-catalyst-review.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-analysis', GIC_DEMO_URL . 'assets/global-impact-catalyst-analysis.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-analysis', GIC_DEMO_URL . 'assets/global-impact-catalyst-analysis.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-reporting', GIC_DEMO_URL . 'assets/global-impact-catalyst-reporting.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-reporting', GIC_DEMO_URL . 'assets/global-impact-catalyst-reporting.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-integration', GIC_DEMO_URL . 'assets/global-impact-catalyst-integration.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-integration', GIC_DEMO_URL . 'assets/global-impact-catalyst-integration.js', array(), GIC_DEMO_VERSION, true);
}
add_action('wp_enqueue_scripts', 'gic_demo_register_assets');

function gic_demo_shortcode($atts = array()) {
    static $instance = 0;
    $instance++;
    $id_prefix = 'gic-' . $instance . '-' . wp_rand(1000, 999999);
    $id = static function ($name) use ($id_prefix) {
        return esc_attr($id_prefix . '-' . $name);
    };

    wp_enqueue_style('global-impact-catalyst-demo');
    wp_enqueue_script('global-impact-catalyst-demo');

    ob_start();
    ?>
    <section class="gic-demo" data-gic-demo>
      <div class="gic-demo__header">
        <p class="gic-demo__eyebrow">Canonical contract engine · v1.1.0</p>
        <h2>Build and Validate an Impact Contract</h2>
        <p>
          Enter facts once. The shared engine creates stable entity identifiers, separates entered facts from derived metrics,
          tests claim eligibility, and exports a versioned impact contract with actionable validation issues.
        </p>
      </div>

      <div class="gic-demo__grid">
        <form class="gic-demo__form" data-gic-form novalidate>
          <div class="gic-demo__errors" data-gic-errors role="alert" tabindex="-1" hidden></div>

          <div class="gic-demo__section-title gic-demo__field--wide"><h3>Context and intended outcome</h3></div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('workspace'); ?>">Workspace</label>
            <input id="<?php echo $id('workspace'); ?>" name="workspace" type="text" required value="Community Impact Portfolio">
          </div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('initiative'); ?>">Initiative or program</label>
            <input id="<?php echo $id('initiative'); ?>" name="initiative" type="text" required value="Community Energy Retrofit Pilot">
          </div>
          <div class="gic-demo__field gic-demo__field--wide">
            <label for="<?php echo $id('goal'); ?>">Impact goal</label>
            <textarea id="<?php echo $id('goal'); ?>" name="goal" rows="2" required>Reduce household energy burden while improving residential efficiency.</textarea>
          </div>
          <div class="gic-demo__field gic-demo__field--wide">
            <label for="<?php echo $id('outcome'); ?>">Outcome</label>
            <textarea id="<?php echo $id('outcome'); ?>" name="outcome" rows="2" required>Participating households experience lower monthly energy costs.</textarea>
          </div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('theme'); ?>">SDG-style theme</label>
            <select id="<?php echo $id('theme'); ?>" name="sdgTheme" required>
              <option>Affordable and clean energy</option><option>Climate action</option><option>Sustainable cities and communities</option>
              <option>Responsible consumption and production</option><option>Good health and well-being</option><option>Quality education</option><option>Reduced inequalities</option>
            </select>
          </div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('geography'); ?>">Geography</label>
            <input id="<?php echo $id('geography'); ?>" name="geography" type="text" value="Chicago, Illinois">
          </div>

          <div class="gic-demo__section-title gic-demo__field--wide"><h3>Indicator definition and measurement</h3></div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('indicator'); ?>">Indicator</label>
            <input id="<?php echo $id('indicator'); ?>" name="indicator" type="text" required value="Average monthly bill reduction">
          </div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('unit'); ?>">Canonical unit</label>
            <input id="<?php echo $id('unit'); ?>" name="unit" type="text" required value="USD">
          </div>
          <div class="gic-demo__field gic-demo__field--wide">
            <label for="<?php echo $id('indicator-definition'); ?>">Indicator definition</label>
            <textarea id="<?php echo $id('indicator-definition'); ?>" name="indicatorDefinition" rows="2" required>Mean reduction in monthly household utility bills relative to the baseline period.</textarea>
          </div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('direction'); ?>">Direction</label>
            <select id="<?php echo $id('direction'); ?>" name="higherIsBetter" required><option value="true" selected>Higher is better</option><option value="false">Lower is better</option></select>
          </div>
          <div class="gic-demo__field">
            <label for="<?php echo $id('population'); ?>">Population group</label>
            <input id="<?php echo $id('population'); ?>" name="populationGroup" type="text" value="Participating households">
          </div>
          <div class="gic-demo__field"><label for="<?php echo $id('baseline-period'); ?>">Baseline period</label><input id="<?php echo $id('baseline-period'); ?>" name="baselinePeriod" type="text" required value="2025 baseline"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('current-period'); ?>">Observation period</label><input id="<?php echo $id('current-period'); ?>" name="currentPeriod" type="text" required value="2026 Q2"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('target-period'); ?>">Target period</label><input id="<?php echo $id('target-period'); ?>" name="targetPeriod" type="text" required value="2027"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('baseline'); ?>">Baseline value</label><input id="<?php echo $id('baseline'); ?>" name="baseline" type="number" required step="0.01" value="0"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('current'); ?>">Observed value</label><input id="<?php echo $id('current'); ?>" name="current" type="number" required step="0.01" value="18"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('target'); ?>">Target value</label><input id="<?php echo $id('target'); ?>" name="target" type="number" required step="0.01" value="30"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('beneficiaries'); ?>">Observed population count</label><input id="<?php echo $id('beneficiaries'); ?>" name="beneficiaries" type="number" step="1" min="0" value="420"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('budget'); ?>">Budget amount</label><input id="<?php echo $id('budget'); ?>" name="budget" type="number" step="0.01" min="0" value="125000"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('budget-currency'); ?>">Budget currency</label><input id="<?php echo $id('budget-currency'); ?>" name="budgetCurrency" type="text" maxlength="3" value="USD"></div>

          <div class="gic-demo__section-title gic-demo__field--wide"><h3>Evidence and method</h3></div>
          <div class="gic-demo__field gic-demo__field--wide"><label for="<?php echo $id('source'); ?>">Source title</label><input id="<?php echo $id('source'); ?>" name="source" type="text" required value="Pilot utility-billing sample and participant survey summary"></div>
          <div class="gic-demo__field gic-demo__field--wide"><label for="<?php echo $id('source-locator'); ?>">Source locator or citation</label><input id="<?php echo $id('source-locator'); ?>" name="sourceLocator" type="text" value="Internal pilot evidence package GIC-ENERGY-2026-Q2"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('method-name'); ?>">Method name</label><input id="<?php echo $id('method-name'); ?>" name="methodName" type="text" value="Before-and-after billing comparison"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('method-version'); ?>">Method version</label><input id="<?php echo $id('method-version'); ?>" name="methodVersion" type="text" value="1.0"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('design-type'); ?>">Design type</label><select id="<?php echo $id('design-type'); ?>" name="designType"><option value="monitoring">Monitoring</option><option value="before_after" selected>Before and after</option><option value="comparison_group">Comparison group</option><option value="quasi_experimental">Quasi-experimental</option><option value="randomized">Randomized</option><option value="qualitative">Qualitative</option><option value="mixed_methods">Mixed methods</option></select></div>
          <div class="gic-demo__field"><label for="<?php echo $id('confidence'); ?>">Confidence</label><select id="<?php echo $id('confidence'); ?>" name="confidence"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></div>
          <div class="gic-demo__field"><label for="<?php echo $id('review'); ?>">Review status</label><select id="<?php echo $id('review'); ?>" name="reviewStatus"><option value="draft">Draft</option><option value="needs_review" selected>Needs review</option><option value="reviewed">Reviewed</option><option value="published">Published</option></select></div>
          <div class="gic-demo__field gic-demo__field--wide"><label for="<?php echo $id('method'); ?>">Method description</label><textarea id="<?php echo $id('method'); ?>" name="method" rows="4" required>Current value is the observed average monthly bill reduction across participating households compared with baseline average bills. Results should be reviewed for seasonality and household-size differences.</textarea></div>

          <div class="gic-demo__section-title gic-demo__field--wide"><h3>Claim governance</h3></div>
          <div class="gic-demo__field"><label for="<?php echo $id('claim-type'); ?>">Claim type</label><select id="<?php echo $id('claim-type'); ?>" name="claimType"><option value="descriptive_observation">Descriptive observation</option><option value="progress_to_target_statement" selected>Progress to target</option><option value="comparison">Comparison</option><option value="contribution_statement">Contribution statement</option><option value="causal_claim">Causal claim</option></select></div>
          <div class="gic-demo__field gic-demo__field--wide"><label for="<?php echo $id('claim-statement'); ?>">Explicit claim statement (required for stronger claims)</label><textarea id="<?php echo $id('claim-statement'); ?>" name="claimStatement" rows="2"></textarea></div>
          <div class="gic-demo__field"><label for="<?php echo $id('comparison-basis'); ?>">Comparison basis</label><input id="<?php echo $id('comparison-basis'); ?>" name="comparisonBasis" type="text"></div>
          <div class="gic-demo__field"><label for="<?php echo $id('contribution-rationale'); ?>">Contribution rationale</label><input id="<?php echo $id('contribution-rationale'); ?>" name="contributionRationale" type="text"></div>
          <div class="gic-demo__field gic-demo__field--wide"><label for="<?php echo $id('causal-design'); ?>">Causal design metadata</label><textarea id="<?php echo $id('causal-design'); ?>" name="causalDesign" rows="2"></textarea></div>

          <div class="gic-demo__actions gic-demo__field--wide">
            <button type="submit">Generate Contract</button><button type="button" data-gic-reset>Reset Example</button><button type="button" data-gic-download>Download JSON</button>
          </div>
        </form>

        <aside class="gic-demo__output" aria-live="polite" aria-atomic="false">
          <div class="gic-demo__scorecard">
            <div><span>Progress to target</span><strong data-gic-progress role="status">—</strong></div>
            <div><span>Documentation / review</span><strong data-gic-quality role="status">—</strong></div>
            <div><span>Validation status</span><strong data-gic-status role="status">—</strong></div>
          </div>
          <div class="gic-demo__bar" aria-hidden="true"><span data-gic-bar></span></div>
          <div class="gic-demo__result" data-gic-result><h3>Impact Contract</h3><p>Generate a contract to inspect facts, metrics, claim eligibility, provenance, and validation.</p></div>
          <details class="gic-demo__json"><summary>View canonical JSON export</summary><pre data-gic-json>{}</pre></details>
        </aside>
      </div>
      <p class="gic-demo__boundary">Educational and public-interest measurement tooling only. Validation is not assurance, certification, audit, causal proof, or automatic truth verification.</p>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('global_impact_catalyst_demo', 'gic_demo_shortcode');

/** Persistent workspace layer introduced in v1.2.0. */
function gic_repository_table($suffix) {
    global $wpdb;
    return $wpdb->prefix . 'gic_' . $suffix;
}

function gic_repository_activate() {
    global $wpdb;
    if (!function_exists('dbDelta')) {
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    }
    $charset = $wpdb->get_charset_collate();
    $contracts = gic_repository_table('contracts');
    $autosaves = gic_repository_table('autosaves');
    $audit = gic_repository_table('audit');
    $sources = gic_repository_table('sources');
    $source_versions = gic_repository_table('source_versions');
    $evidence = gic_repository_table('evidence');
    $datasets = gic_repository_table('datasets');
    $provenance = gic_repository_table('provenance');
    $claim_evidence = gic_repository_table('claim_evidence');
    $units = gic_repository_table('units');
    $indicator_definitions = gic_repository_table('indicator_definitions');
    $indicator_versions = gic_repository_table('indicator_versions');
    $baseline_models = gic_repository_table('baseline_models');
    $baseline_versions = gic_repository_table('baseline_versions');
    $target_models = gic_repository_table('target_models');
    $target_versions = gic_repository_table('target_versions');
    $method_definitions = gic_repository_table('method_definitions');
    $method_versions = gic_repository_table('method_versions');
    $indicator_bindings = gic_repository_table('indicator_bindings');
    dbDelta("CREATE TABLE {$contracts} (
      record_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      workspace_name text NOT NULL,
      initiative_name text NOT NULL,
      contract_version varchar(24) NOT NULL,
      lifecycle_status varchar(32) NOT NULL DEFAULT 'draft',
      save_state varchar(16) NOT NULL DEFAULT 'saved',
      revision bigint unsigned NOT NULL DEFAULT 1,
      content_hash char(64) NOT NULL,
      archived_at datetime NULL,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      contract_json longtext NOT NULL,
      PRIMARY KEY  (record_id),
      UNIQUE KEY initiative_id (initiative_id),
      KEY workspace_id (workspace_id),
      KEY updated_at (updated_at)
    ) {$charset};");
    dbDelta("CREATE TABLE {$autosaves} (
      initiative_id varchar(96) NOT NULL,
      record_id varchar(96) NOT NULL,
      base_revision bigint unsigned NOT NULL DEFAULT 0,
      content_hash char(64) NOT NULL,
      saved_at datetime NOT NULL,
      contract_json longtext NOT NULL,
      PRIMARY KEY  (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$audit} (
      audit_id bigint unsigned NOT NULL AUTO_INCREMENT,
      occurred_at datetime NOT NULL,
      user_id bigint unsigned NOT NULL DEFAULT 0,
      action varchar(40) NOT NULL,
      record_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 0,
      details_json longtext NOT NULL,
      PRIMARY KEY  (audit_id),
      KEY record_id (record_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$sources} (
      source_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL DEFAULT '',
      title text NOT NULL,
      source_type varchar(40) NOT NULL DEFAULT 'document',
      locator text NOT NULL,
      url text NOT NULL,
      doi varchar(255) NOT NULL DEFAULT '',
      license varchar(120) NOT NULL DEFAULT 'not_recorded',
      access_rights varchar(80) NOT NULL DEFAULT 'not_recorded',
      current_version bigint unsigned NOT NULL DEFAULT 0,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (source_id),
      KEY workspace_id (workspace_id),
      KEY initiative_id (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$source_versions} (
      source_version_id varchar(96) NOT NULL,
      source_id varchar(96) NOT NULL,
      version_number bigint unsigned NOT NULL,
      version_label varchar(120) NOT NULL,
      content_hash char(64) NOT NULL,
      checksum_algorithm varchar(20) NOT NULL DEFAULT 'sha256',
      checksum_value char(64) NOT NULL,
      mime_type varchar(120) NOT NULL DEFAULT 'application/json',
      size_bytes bigint unsigned NULL,
      captured_at datetime NOT NULL,
      captured_by bigint unsigned NOT NULL DEFAULT 0,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (source_version_id),
      UNIQUE KEY source_checksum (source_id,checksum_value),
      KEY source_id (source_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$evidence} (
      evidence_id varchar(96) NOT NULL,
      source_id varchar(96) NOT NULL,
      source_version_id varchar(96) NOT NULL DEFAULT '',
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL DEFAULT '',
      evidence_type varchar(40) NOT NULL DEFAULT 'excerpt',
      title text NOT NULL,
      locator text NOT NULL,
      exact_quote longtext NOT NULL,
      paraphrase longtext NOT NULL,
      notes longtext NOT NULL,
      content_hash char(64) NOT NULL,
      captured_at datetime NOT NULL,
      captured_by bigint unsigned NOT NULL DEFAULT 0,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (evidence_id),
      KEY source_id (source_id),
      KEY initiative_id (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$datasets} (
      dataset_id varchar(96) NOT NULL,
      source_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL DEFAULT '',
      title text NOT NULL,
      version varchar(120) NOT NULL DEFAULT '',
      license varchar(120) NOT NULL DEFAULT 'not_recorded',
      checksum_algorithm varchar(20) NOT NULL DEFAULT 'sha256',
      checksum_value char(64) NOT NULL,
      schema_fingerprint char(64) NOT NULL DEFAULT '',
      temporal_coverage text NOT NULL,
      spatial_coverage text NOT NULL,
      row_count bigint unsigned NULL,
      column_count bigint unsigned NULL,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (dataset_id),
      KEY source_id (source_id),
      KEY initiative_id (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$provenance} (
      edge_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL DEFAULT '',
      subject_type varchar(40) NOT NULL,
      subject_id varchar(96) NOT NULL,
      predicate varchar(60) NOT NULL,
      object_type varchar(40) NOT NULL,
      object_id varchar(96) NOT NULL,
      process_name text NOT NULL,
      method_id varchar(96) NOT NULL DEFAULT '',
      method_version varchar(80) NOT NULL DEFAULT '',
      occurred_at datetime NOT NULL,
      actor bigint unsigned NOT NULL DEFAULT 0,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (edge_id),
      KEY initiative_id (initiative_id),
      KEY subject_id (subject_id),
      KEY object_id (object_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$claim_evidence} (
      claim_id varchar(96) NOT NULL,
      evidence_id varchar(96) NOT NULL,
      relationship varchar(24) NOT NULL DEFAULT 'supports',
      strength varchar(24) NOT NULL DEFAULT 'direct',
      notes longtext NOT NULL,
      linked_at datetime NOT NULL,
      linked_by bigint unsigned NOT NULL DEFAULT 0,
      PRIMARY KEY  (claim_id,evidence_id,relationship),
      KEY evidence_id (evidence_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$units} (
      unit_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL DEFAULT '',
      code varchar(80) NOT NULL,
      symbol varchar(40) NOT NULL DEFAULT '',
      name text NOT NULL,
      dimension varchar(80) NOT NULL,
      canonical_unit_id varchar(96) NOT NULL,
      scale_to_canonical double NOT NULL DEFAULT 1,
      offset_to_canonical double NOT NULL DEFAULT 0,
      precision_digits smallint unsigned NOT NULL DEFAULT 2,
      lifecycle_status varchar(24) NOT NULL DEFAULT 'active',
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (unit_id),
      UNIQUE KEY workspace_code (workspace_id,code),
      KEY dimension (dimension)
    ) {$charset};");
    dbDelta("CREATE TABLE {$indicator_definitions} (
      indicator_definition_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      name text NOT NULL,
      description longtext NOT NULL,
      direction varchar(32) NOT NULL DEFAULT 'higher_is_better',
      unit_id varchar(96) NOT NULL,
      aggregation_method varchar(32) NOT NULL DEFAULT 'latest',
      formula_expression longtext NOT NULL,
      formula_language varchar(40) NOT NULL DEFAULT 'gic-expression-1.0',
      disaggregation_json longtext NOT NULL,
      quality_profile_json longtext NOT NULL,
      lifecycle_status varchar(24) NOT NULL DEFAULT 'draft',
      current_version bigint unsigned NOT NULL DEFAULT 0,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (indicator_definition_id),
      KEY workspace_id (workspace_id),
      KEY unit_id (unit_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$indicator_versions} (
      indicator_definition_version_id varchar(96) NOT NULL,
      indicator_definition_id varchar(96) NOT NULL,
      version_number bigint unsigned NOT NULL,
      version_label varchar(80) NOT NULL,
      definition_hash char(64) NOT NULL,
      definition_json longtext NOT NULL,
      created_at datetime NOT NULL,
      created_by bigint unsigned NOT NULL DEFAULT 0,
      PRIMARY KEY  (indicator_definition_version_id),
      UNIQUE KEY definition_hash (indicator_definition_id,definition_hash),
      KEY indicator_definition_id (indicator_definition_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$baseline_models} (
      baseline_model_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      name text NOT NULL,
      method_type varchar(32) NOT NULL,
      unit_id varchar(96) NOT NULL,
      description longtext NOT NULL,
      benchmark_value double NULL,
      rolling_periods bigint unsigned NULL,
      formula_expression longtext NOT NULL,
      minimum_observations bigint unsigned NOT NULL DEFAULT 1,
      confidence varchar(24) NOT NULL DEFAULT 'medium',
      parameters_json longtext NOT NULL,
      lifecycle_status varchar(24) NOT NULL DEFAULT 'draft',
      current_version bigint unsigned NOT NULL DEFAULT 0,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (baseline_model_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$baseline_versions} (
      baseline_model_version_id varchar(96) NOT NULL,
      baseline_model_id varchar(96) NOT NULL,
      version_number bigint unsigned NOT NULL,
      version_label varchar(80) NOT NULL,
      model_hash char(64) NOT NULL,
      model_json longtext NOT NULL,
      created_at datetime NOT NULL,
      created_by bigint unsigned NOT NULL DEFAULT 0,
      PRIMARY KEY  (baseline_model_version_id),
      UNIQUE KEY model_hash (baseline_model_id,model_hash),
      KEY baseline_model_id (baseline_model_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$target_models} (
      target_model_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      indicator_definition_id varchar(96) NOT NULL DEFAULT '',
      name text NOT NULL,
      target_type varchar(32) NOT NULL,
      unit_id varchar(96) NOT NULL,
      direction varchar(32) NOT NULL DEFAULT 'higher_is_better',
      target_value double NULL,
      lower_value double NULL,
      upper_value double NULL,
      relative_change_percent double NULL,
      start_period text NULL,
      end_period text NULL,
      start_value double NULL,
      end_value double NULL,
      trajectory_type varchar(24) NOT NULL DEFAULT 'linear',
      formula_expression longtext NOT NULL,
      milestones_json longtext NOT NULL,
      lifecycle_status varchar(24) NOT NULL DEFAULT 'draft',
      current_version bigint unsigned NOT NULL DEFAULT 0,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (target_model_id),
      KEY workspace_id (workspace_id),
      KEY indicator_definition_id (indicator_definition_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$target_versions} (
      target_model_version_id varchar(96) NOT NULL,
      target_model_id varchar(96) NOT NULL,
      version_number bigint unsigned NOT NULL,
      version_label varchar(80) NOT NULL,
      model_hash char(64) NOT NULL,
      model_json longtext NOT NULL,
      created_at datetime NOT NULL,
      created_by bigint unsigned NOT NULL DEFAULT 0,
      PRIMARY KEY  (target_model_version_id),
      UNIQUE KEY model_hash (target_model_id,model_hash),
      KEY target_model_id (target_model_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$method_definitions} (
      method_definition_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      name text NOT NULL,
      method_kind varchar(32) NOT NULL DEFAULT 'measurement',
      design_type varchar(40) NOT NULL DEFAULT 'monitoring',
      description longtext NOT NULL,
      formula_expression longtext NOT NULL,
      input_requirements_json longtext NOT NULL,
      quality_profile_json longtext NOT NULL,
      limitations_json longtext NOT NULL,
      lifecycle_status varchar(24) NOT NULL DEFAULT 'draft',
      current_version bigint unsigned NOT NULL DEFAULT 0,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (method_definition_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$method_versions} (
      method_definition_version_id varchar(96) NOT NULL,
      method_definition_id varchar(96) NOT NULL,
      version_number bigint unsigned NOT NULL,
      version_label varchar(80) NOT NULL,
      method_hash char(64) NOT NULL,
      method_json longtext NOT NULL,
      created_at datetime NOT NULL,
      created_by bigint unsigned NOT NULL DEFAULT 0,
      PRIMARY KEY  (method_definition_version_id),
      UNIQUE KEY method_hash (method_definition_id,method_hash),
      KEY method_definition_id (method_definition_id)
    ) {$charset};");
    dbDelta("CREATE TABLE {$indicator_bindings} (
      binding_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      indicator_id varchar(96) NOT NULL,
      indicator_definition_id varchar(96) NOT NULL,
      indicator_definition_version_id varchar(96) NOT NULL,
      unit_id varchar(96) NOT NULL,
      baseline_model_id varchar(96) NOT NULL DEFAULT '',
      baseline_model_version_id varchar(96) NOT NULL DEFAULT '',
      target_model_id varchar(96) NOT NULL DEFAULT '',
      target_model_version_id varchar(96) NOT NULL DEFAULT '',
      method_definition_id varchar(96) NOT NULL DEFAULT '',
      method_definition_version_id varchar(96) NOT NULL DEFAULT '',
      bound_at datetime NOT NULL,
      bound_by bigint unsigned NOT NULL DEFAULT 0,
      revision bigint unsigned NOT NULL DEFAULT 1,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (binding_id),
      UNIQUE KEY initiative_indicator (initiative_id,indicator_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");

    dbDelta("CREATE TABLE " . gic_repository_table('impact_results') . " (
      result_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      result_type varchar(32) NOT NULL,
      name text NOT NULL,
      description longtext NOT NULL,
      indicator_definition_id varchar(96) NOT NULL DEFAULT '',
      lifecycle_status varchar(24) NOT NULL DEFAULT 'draft',
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (result_id),
      KEY workspace_id (workspace_id),
      KEY initiative_id (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('result_relationships') . " (
      relationship_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      from_result_id varchar(96) NOT NULL,
      to_result_id varchar(96) NOT NULL,
      relationship_type varchar(40) NOT NULL,
      contribution_weight double NULL,
      notes longtext NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (relationship_id),
      UNIQUE KEY result_relationship (from_result_id,to_result_id,relationship_type),
      KEY initiative_id (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('observation_series') . " (
      observation_record_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      indicator_id varchar(96) NOT NULL,
      indicator_definition_id varchar(96) NOT NULL DEFAULT '',
      impact_result_id varchar(96) NOT NULL DEFAULT '',
      period_start varchar(40) NULL,
      period_end varchar(40) NULL,
      period_label varchar(160) NOT NULL,
      value double NULL,
      unit_id varchar(96) NOT NULL,
      data_state varchar(24) NOT NULL DEFAULT 'complete',
      revision_of_observation_id varchar(96) NOT NULL DEFAULT '',
      received_at datetime NOT NULL,
      revised_at datetime NULL,
      source_id varchar(96) NOT NULL DEFAULT '',
      method_definition_id varchar(96) NOT NULL DEFAULT '',
      dimensions_json longtext NOT NULL,
      denominator_json longtext NOT NULL,
      notes longtext NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (observation_record_id),
      KEY initiative_indicator (initiative_id,indicator_id),
      KEY workspace_state (workspace_id,data_state),
      KEY period_label (period_label)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('beneficiary_definitions') . " (
      beneficiary_definition_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      name text NOT NULL,
      description longtext NOT NULL,
      reach_type varchar(24) NOT NULL DEFAULT 'direct',
      counting_method varchar(32) NOT NULL DEFAULT 'unique',
      privacy_level varchar(32) NOT NULL DEFAULT 'aggregate_only',
      overlap_policy varchar(32) NOT NULL DEFAULT 'unknown',
      overlap_notes longtext NOT NULL,
      lifecycle_status varchar(24) NOT NULL DEFAULT 'draft',
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (beneficiary_definition_id),
      KEY initiative_id (initiative_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('beneficiary_observations') . " (
      beneficiary_observation_id varchar(96) NOT NULL,
      beneficiary_definition_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      period_start varchar(40) NULL,
      period_end varchar(40) NULL,
      period_label varchar(160) NOT NULL,
      observed_count double NULL,
      data_state varchar(24) NOT NULL DEFAULT 'complete',
      revision_of_observation_id varchar(96) NOT NULL DEFAULT '',
      dimensions_json longtext NOT NULL,
      overlap_estimate double NULL,
      denominator_notes longtext NOT NULL,
      source_id varchar(96) NOT NULL DEFAULT '',
      received_at datetime NOT NULL,
      revised_at datetime NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (beneficiary_observation_id),
      KEY definition_period (beneficiary_definition_id,period_label),
      KEY workspace_state (workspace_id,data_state)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('financial_records') . " (
      financial_record_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      record_type varchar(24) NOT NULL,
      funding_source text NOT NULL,
      cost_category varchar(120) NOT NULL DEFAULT 'uncategorized',
      period_start varchar(40) NULL,
      period_end varchar(40) NULL,
      period_label varchar(160) NOT NULL,
      amount double NULL,
      currency varchar(12) NOT NULL,
      reporting_currency varchar(12) NOT NULL,
      exchange_rate double NULL,
      reporting_amount double NULL,
      data_state varchar(24) NOT NULL DEFAULT 'complete',
      source_id varchar(96) NOT NULL DEFAULT '',
      notes longtext NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (financial_record_id),
      KEY initiative_period (initiative_id,period_label),
      KEY workspace_currency (workspace_id,reporting_currency)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('external_factors') . " (
      external_factor_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      name text NOT NULL,
      description longtext NOT NULL,
      direction varchar(24) NOT NULL DEFAULT 'unknown',
      influence_level varchar(24) NOT NULL DEFAULT 'unknown',
      period_start varchar(40) NULL,
      period_end varchar(40) NULL,
      period_label varchar(160) NOT NULL DEFAULT '',
      source_id varchar(96) NOT NULL DEFAULT '',
      notes longtext NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (external_factor_id),
      KEY initiative_id (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('contribution_notes') . " (
      contribution_note_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      impact_result_id varchar(96) NOT NULL DEFAULT '',
      statement longtext NOT NULL,
      contribution_type varchar(24) NOT NULL DEFAULT 'unknown',
      evidence_refs_json longtext NOT NULL,
      external_factor_refs_json longtext NOT NULL,
      limitations longtext NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (contribution_note_id),
      KEY initiative_id (initiative_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('outcome_portfolios') . " (
      outcome_portfolio_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      name text NOT NULL,
      description longtext NOT NULL,
      aggregation_method varchar(24) NOT NULL DEFAULT 'sum',
      target_unit_id varchar(96) NOT NULL DEFAULT '',
      period_policy varchar(24) NOT NULL DEFAULT 'exact',
      overlap_policy varchar(48) NOT NULL DEFAULT 'exclude_unknown_or_overlapping',
      missing_data_policy varchar(32) NOT NULL DEFAULT 'exclude_and_disclose',
      archived_at datetime NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (outcome_portfolio_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('outcome_portfolio_members') . " (
      outcome_portfolio_id varchar(96) NOT NULL,
      membership_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      indicator_id varchar(96) NOT NULL,
      indicator_definition_id varchar(96) NOT NULL DEFAULT '',
      impact_result_id varchar(96) NOT NULL DEFAULT '',
      population_scope text NOT NULL,
      overlap_group varchar(160) NOT NULL DEFAULT '',
      denominator_definition longtext NOT NULL,
      weight double NOT NULL DEFAULT 1,
      position bigint unsigned NOT NULL DEFAULT 0,
      added_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (outcome_portfolio_id,membership_id),
      KEY initiative_indicator (initiative_id,indicator_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('portfolio_aggregation_runs') . " (
      aggregation_run_id varchar(96) NOT NULL,
      outcome_portfolio_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      period_start varchar(40) NULL,
      period_end varchar(40) NULL,
      period_label varchar(160) NOT NULL,
      aggregation_method varchar(24) NOT NULL,
      target_unit_id varchar(96) NOT NULL DEFAULT '',
      result_value double NULL,
      result_json longtext NOT NULL,
      created_at datetime NOT NULL,
      created_by bigint unsigned NOT NULL DEFAULT 0,
      PRIMARY KEY  (aggregation_run_id),
      KEY outcome_portfolio_id (outcome_portfolio_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('workflow_roles') . " (
      role_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      name text NOT NULL,
      description longtext NOT NULL,
      permissions_json longtext NOT NULL,
      is_system tinyint unsigned NOT NULL DEFAULT 0,
      archived_at datetime NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (role_id),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('review_assignments') . " (
      assignment_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      subject_type varchar(48) NOT NULL,
      subject_id varchar(96) NOT NULL,
      reviewer_id varchar(190) NOT NULL,
      role_id varchar(96) NOT NULL,
      status varchar(32) NOT NULL DEFAULT 'pending',
      priority varchar(16) NOT NULL DEFAULT 'normal',
      due_at datetime NULL,
      assigned_by varchar(190) NOT NULL,
      assigned_at datetime NOT NULL,
      started_at datetime NULL,
      completed_at datetime NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (assignment_id),
      KEY workspace_status (workspace_id,status),
      KEY reviewer_status (reviewer_id,status)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('review_comments') . " (
      comment_id varchar(96) NOT NULL,
      assignment_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      subject_type varchar(48) NOT NULL,
      subject_id varchar(96) NOT NULL,
      author_id varchar(190) NOT NULL,
      parent_comment_id varchar(96) NOT NULL DEFAULT '',
      visibility varchar(24) NOT NULL DEFAULT 'workspace',
      body longtext NOT NULL,
      resolution_status varchar(24) NOT NULL DEFAULT 'open',
      resolved_by varchar(190) NOT NULL DEFAULT '',
      resolved_at datetime NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (comment_id),
      KEY assignment_status (assignment_id,resolution_status)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('quality_assessments') . " (
      assessment_id varchar(96) NOT NULL,
      assignment_id varchar(96) NOT NULL DEFAULT '',
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      subject_type varchar(48) NOT NULL,
      subject_id varchar(96) NOT NULL,
      rubric_id varchar(96) NOT NULL,
      rubric_version varchar(32) NOT NULL,
      assessor_id varchar(190) NOT NULL,
      status varchar(24) NOT NULL DEFAULT 'submitted',
      score double NOT NULL,
      maximum_score double NOT NULL DEFAULT 100,
      grade varchar(24) NOT NULL,
      dimensions_json longtext NOT NULL,
      findings_json longtext NOT NULL,
      limitations longtext NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      submitted_at datetime NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (assessment_id),
      KEY subject_status (subject_type,subject_id,status)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('approval_decisions') . " (
      decision_id varchar(96) NOT NULL,
      assignment_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      subject_type varchar(48) NOT NULL,
      subject_id varchar(96) NOT NULL,
      reviewer_id varchar(190) NOT NULL,
      decision varchar(24) NOT NULL,
      rationale longtext NOT NULL,
      conditions_json longtext NOT NULL,
      decided_at datetime NOT NULL,
      supersedes_decision_id varchar(96) NOT NULL DEFAULT '',
      revision bigint unsigned NOT NULL DEFAULT 1,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (decision_id),
      KEY subject_id (subject_type,subject_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('workflow_revisions') . " (
      workflow_revision_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      subject_type varchar(48) NOT NULL,
      subject_id varchar(96) NOT NULL,
      revision_number bigint unsigned NOT NULL,
      change_type varchar(32) NOT NULL,
      actor_id varchar(190) NOT NULL,
      summary longtext NOT NULL,
      previous_content_hash char(64) NOT NULL DEFAULT '',
      content_hash char(64) NOT NULL,
      snapshot_json longtext NOT NULL,
      created_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (workflow_revision_id),
      UNIQUE KEY subject_revision (subject_type,subject_id,revision_number),
      KEY workspace_id (workspace_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('correction_records') . " (
      correction_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      subject_type varchar(48) NOT NULL,
      subject_id varchar(96) NOT NULL,
      severity varchar(24) NOT NULL DEFAULT 'minor',
      status varchar(24) NOT NULL DEFAULT 'open',
      reason longtext NOT NULL,
      proposed_changes_json longtext NOT NULL,
      opened_by varchar(190) NOT NULL,
      opened_at datetime NOT NULL,
      applied_by varchar(190) NOT NULL DEFAULT '',
      applied_at datetime NULL,
      resulting_revision_id varchar(96) NOT NULL DEFAULT '',
      resolution_notes longtext NOT NULL,
      revision bigint unsigned NOT NULL DEFAULT 1,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (correction_id),
      KEY subject_status (subject_type,subject_id,status)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('publication_records') . " (
      publication_id varchar(96) NOT NULL,
      workspace_id varchar(96) NOT NULL,
      initiative_id varchar(96) NOT NULL,
      subject_type varchar(48) NOT NULL,
      subject_id varchar(96) NOT NULL,
      title text NOT NULL,
      publication_status varchar(24) NOT NULL DEFAULT 'draft',
      release_label varchar(160) NOT NULL DEFAULT '',
      public_url text NOT NULL,
      approved_decision_id varchar(96) NOT NULL DEFAULT '',
      quality_assessment_id varchar(96) NOT NULL DEFAULT '',
      content_hash char(64) NOT NULL,
      published_revision_id varchar(96) NOT NULL DEFAULT '',
      published_at datetime NULL,
      published_by varchar(190) NOT NULL DEFAULT '',
      withdrawn_at datetime NULL,
      withdrawn_by varchar(190) NOT NULL DEFAULT '',
      withdrawal_reason longtext NOT NULL,
      supersedes_publication_id varchar(96) NOT NULL DEFAULT '',
      revision bigint unsigned NOT NULL DEFAULT 1,
      created_at datetime NOT NULL,
      updated_at datetime NOT NULL,
      metadata_json longtext NOT NULL,
      PRIMARY KEY  (publication_id),
      KEY workspace_status (workspace_id,publication_status)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('publication_events') . " (
      publication_event_id varchar(96) NOT NULL,
      publication_id varchar(96) NOT NULL,
      event_type varchar(32) NOT NULL,
      actor_id varchar(190) NOT NULL,
      reason longtext NOT NULL,
      event_at datetime NOT NULL,
      details_json longtext NOT NULL,
      PRIMARY KEY  (publication_event_id),
      KEY publication_id (publication_id)
    ) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_benchmarks') . " (benchmark_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, indicator_id varchar(96) NOT NULL, name text NOT NULL, value decimal(30,10) NOT NULL, unit_id varchar(96) NOT NULL, period_label varchar(160) NOT NULL DEFAULT '', geography text NOT NULL, population text NOT NULL, quality_status varchar(32) NOT NULL DEFAULT 'not_assessed', revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (benchmark_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_comparison_sets') . " (comparison_set_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, indicator_id varchar(96) NOT NULL, name text NOT NULL, policy_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (comparison_set_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_comparison_members') . " (comparison_member_id varchar(96) NOT NULL, comparison_set_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', benchmark_id varchar(96) NOT NULL DEFAULT '', label text NOT NULL, value_override decimal(30,10) NULL, unit_id varchar(96) NOT NULL DEFAULT '', metadata_json longtext NOT NULL, PRIMARY KEY (comparison_member_id), KEY comparison_set_id (comparison_set_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_scenarios') . " (scenario_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL, indicator_id varchar(96) NOT NULL, name text NOT NULL, model_type varchar(32) NOT NULL, periods int unsigned NOT NULL DEFAULT 1, base_value decimal(30,10) NULL, unit_id varchar(96) NOT NULL, parameters_json longtext NOT NULL, assumptions_json longtext NOT NULL, limitations_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (scenario_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_uncertainty_models') . " (uncertainty_model_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, name text NOT NULL, uncertainty_type varchar(32) NOT NULL, absolute_margin decimal(30,10) NULL, relative_margin_percent decimal(20,8) NULL, lower_bound decimal(30,10) NULL, upper_bound decimal(30,10) NULL, confidence_level decimal(8,6) NOT NULL DEFAULT .95, distribution varchar(48) NOT NULL DEFAULT 'bounded', assumptions_json longtext NOT NULL, limitations_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (uncertainty_model_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_runs') . " (analysis_run_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', analysis_type varchar(48) NOT NULL, subject_id varchar(96) NOT NULL, input_hash char(64) NOT NULL, result_hash char(64) NOT NULL, result_json longtext NOT NULL, created_by varchar(190) NOT NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (analysis_run_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_sensitivity_runs') . " (sensitivity_run_id varchar(96) NOT NULL, scenario_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL, parameter_name varchar(120) NOT NULL, absolute_effect decimal(30,10) NOT NULL, rank_order int unsigned NOT NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (sensitivity_run_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('report_templates') . " (template_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, name text NOT NULL, report_type varchar(48) NOT NULL, sections_json longtext NOT NULL, citation_style varchar(32) NOT NULL, accessibility_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (template_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('report_documents') . " (report_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL, template_id varchar(96) NOT NULL DEFAULT '', title text NOT NULL, report_type varchar(48) NOT NULL, audience varchar(48) NOT NULL, period_label varchar(160) NOT NULL DEFAULT '', source_bundle_hash char(64) NOT NULL, content_hash char(64) NOT NULL, document_json longtext NOT NULL, rendered_markdown longtext NOT NULL, rendered_html longtext NOT NULL, citations_json longtext NOT NULL, methodology_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (report_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('dashboard_definitions') . " (dashboard_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', name text NOT NULL, audience varchar(48) NOT NULL, layout_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (dashboard_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('dashboard_cards') . " (card_id varchar(96) NOT NULL, dashboard_id varchar(96) NOT NULL, card_type varchar(48) NOT NULL, title text NOT NULL, subject_type varchar(48) NOT NULL DEFAULT '', subject_id varchar(96) NOT NULL DEFAULT '', position int NOT NULL DEFAULT 0, alt_text text NOT NULL, configuration_json longtext NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (card_id), KEY dashboard_id (dashboard_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('publication_snapshots') . " (snapshot_id varchar(96) NOT NULL, publication_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL, report_id varchar(96) NOT NULL DEFAULT '', snapshot_hash char(64) NOT NULL, snapshot_json longtext NOT NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (snapshot_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('export_bundles') . " (export_bundle_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', report_id varchar(96) NOT NULL DEFAULT '', publication_snapshot_id varchar(96) NOT NULL DEFAULT '', manifest_hash char(64) NOT NULL, archive_hash char(64) NOT NULL DEFAULT '', artifact_count int unsigned NOT NULL DEFAULT 0, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (export_bundle_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('export_artifacts') . " (artifact_id varchar(96) NOT NULL, export_bundle_id varchar(96) NOT NULL, artifact_path text NOT NULL, media_type varchar(120) NOT NULL, byte_size bigint unsigned NOT NULL, sha256 char(64) NOT NULL, content_text longtext NOT NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (artifact_id), KEY export_bundle_id (export_bundle_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('api_clients') . " (client_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL DEFAULT '', name text NOT NULL, client_type varchar(32) NOT NULL DEFAULT 'service', lifecycle_status varchar(24) NOT NULL DEFAULT 'active', rate_limit_per_minute int unsigned NOT NULL DEFAULT 60, scopes_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (client_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('api_keys') . " (api_key_id varchar(96) NOT NULL, client_id varchar(96) NOT NULL, key_prefix varchar(32) NOT NULL, key_hash char(64) NOT NULL, scopes_json longtext NOT NULL, expires_at datetime NULL, revoked_at datetime NULL, last_used_at datetime NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (api_key_id), UNIQUE KEY key_hash (key_hash), KEY client_id (client_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('api_access_log') . " (access_id varchar(96) NOT NULL, client_id varchar(96) NOT NULL DEFAULT '', workspace_id varchar(96) NOT NULL DEFAULT '', operation varchar(96) NOT NULL, resource_type varchar(48) NOT NULL DEFAULT '', resource_id varchar(96) NOT NULL DEFAULT '', scope_name varchar(96) NOT NULL DEFAULT '', status_code int unsigned NOT NULL, occurred_at datetime NOT NULL, request_hash char(64) NOT NULL DEFAULT '', response_hash char(64) NOT NULL DEFAULT '', metadata_json longtext NOT NULL, PRIMARY KEY (access_id), KEY workspace_id (workspace_id), KEY client_id (client_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('embed_definitions') . " (embed_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', publication_id varchar(96) NOT NULL, publication_snapshot_id varchar(96) NOT NULL, embed_type varchar(48) NOT NULL, title text NOT NULL, public_slug varchar(190) NOT NULL, configuration_json longtext NOT NULL, accessibility_json longtext NOT NULL, content_hash char(64) NOT NULL, lifecycle_status varchar(24) NOT NULL DEFAULT 'active', revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (embed_id), UNIQUE KEY public_slug (public_slug), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('platform_handoffs') . " (handoff_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', destination varchar(64) NOT NULL, handoff_version varchar(24) NOT NULL, status varchar(24) NOT NULL DEFAULT 'ready', source_snapshot_hash char(64) NOT NULL, payload_hash char(64) NOT NULL, payload_json longtext NOT NULL, idempotency_key varchar(190) NOT NULL DEFAULT '', created_at datetime NOT NULL, delivered_at datetime NULL, delivery_receipt_json longtext NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (handoff_id), KEY workspace_destination (workspace_id,destination), UNIQUE KEY idempotent_handoff (workspace_id,destination,idempotency_key)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('integration_events') . " (event_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL DEFAULT '', initiative_id varchar(96) NOT NULL DEFAULT '', event_type varchar(96) NOT NULL, event_version varchar(24) NOT NULL, subject_type varchar(48) NOT NULL, subject_id varchar(96) NOT NULL, payload_hash char(64) NOT NULL, payload_json longtext NOT NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (event_id), KEY workspace_id (workspace_id)) {$charset};");
    gic_registry_seed_units();
    update_option('gic_repository_schema_version', 10, false);
}
register_activation_hook(__FILE__, 'gic_repository_activate');

function gic_repository_maybe_upgrade() {
    if ((int) get_option('gic_repository_schema_version', 0) < 10) { gic_repository_activate(); }
}
add_action('plugins_loaded', 'gic_repository_maybe_upgrade');

function gic_repository_can_edit() {
    return current_user_can('edit_posts');
}

function gic_repository_hash($contract) {
    return hash('sha256', wp_json_encode($contract, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
}

function gic_repository_audit($action, $contract, $revision, $details = array()) {
    global $wpdb;
    $wpdb->insert(gic_repository_table('audit'), array(
        'occurred_at' => current_time('mysql', true),
        'user_id' => get_current_user_id(),
        'action' => sanitize_key($action),
        'record_id' => sanitize_text_field($contract['record_id'] ?? ''),
        'workspace_id' => sanitize_text_field($contract['facts']['workspace']['id'] ?? ''),
        'initiative_id' => sanitize_text_field($contract['facts']['initiative']['id'] ?? ''),
        'revision' => (int) $revision,
        'details_json' => wp_json_encode($details),
    ), array('%s','%d','%s','%s','%s','%s','%d','%s'));
}

function gic_repository_normalize_workspace(&$contract) {
    global $wpdb;
    $table = gic_repository_table('contracts');
    $name = sanitize_text_field($contract['facts']['workspace']['name'] ?? '');
    if ($name === '') { return; }
    $row = $wpdb->get_row($wpdb->prepare(
        "SELECT workspace_id, contract_json FROM {$table} WHERE LOWER(workspace_name)=LOWER(%s) AND archived_at IS NULL ORDER BY updated_at DESC LIMIT 1",
        $name
    ), ARRAY_A);
    if ($row) {
        $stored = json_decode($row['contract_json'], true);
        if (is_array($stored) && isset($stored['facts']['workspace'])) {
            $contract['facts']['workspace'] = $stored['facts']['workspace'];
            $contract['facts']['initiative']['workspace_id'] = $row['workspace_id'];
        }
    }
}

function gic_repository_validate_contract($contract) {
    if (!is_array($contract) || ($contract['contract_type'] ?? '') !== 'global_impact_contract') {
        return new WP_Error('gic_invalid_contract', 'A canonical Global Impact Catalyst contract is required.', array('status' => 400));
    }
    foreach (array('record_id') as $key) {
        if (empty($contract[$key])) {
            return new WP_Error('gic_missing_identifier', 'The contract is missing a stable record identifier.', array('status' => 400));
        }
    }
    if (empty($contract['facts']['workspace']['id']) || empty($contract['facts']['initiative']['id'])) {
        return new WP_Error('gic_missing_entity_identifier', 'Workspace and initiative identifiers are required.', array('status' => 400));
    }
    return true;
}

function gic_repository_save_contract(WP_REST_Request $request) {
    global $wpdb;
    $contract = $request->get_json_params();
    $valid = gic_repository_validate_contract($contract);
    if (is_wp_error($valid)) { return $valid; }
    gic_repository_normalize_workspace($contract);
    $table = gic_repository_table('contracts');
    $record_id = sanitize_text_field($contract['record_id']);
    $existing = $wpdb->get_row($wpdb->prepare("SELECT revision, created_at, content_hash, workspace_id, initiative_id, updated_at FROM {$table} WHERE record_id=%s", $record_id), ARRAY_A);
    $expected = $request->get_param('expected_revision');
    $actual = $existing ? (int) $existing['revision'] : 0;
    $incoming_hash = gic_repository_hash($contract);
    if ($existing && (int) $expected === 0 && hash_equals($existing['content_hash'], $incoming_hash)) {
        return rest_ensure_response(array('contract' => $contract, 'repository' => array(
            'record_id' => $record_id, 'workspace_id' => $existing['workspace_id'], 'initiative_id' => $existing['initiative_id'],
            'revision' => $actual, 'content_hash' => $incoming_hash, 'save_state' => 'saved',
            'updated_at' => $existing['updated_at'], 'status' => 'unchanged',
        )));
    }
    if ($expected !== null && (int) $expected !== $actual) {
        return new WP_Error('gic_revision_conflict', 'This initiative was changed by another session.', array(
            'status' => 409, 'expected_revision' => (int) $expected, 'actual_revision' => $actual,
        ));
    }
    $revision = $actual + 1;
    $now = current_time('mysql', true);
    $data = array(
        'record_id' => $record_id,
        'workspace_id' => sanitize_text_field($contract['facts']['workspace']['id']),
        'initiative_id' => sanitize_text_field($contract['facts']['initiative']['id']),
        'workspace_name' => sanitize_text_field($contract['facts']['workspace']['name'] ?? ''),
        'initiative_name' => sanitize_text_field($contract['facts']['initiative']['name'] ?? ''),
        'contract_version' => sanitize_text_field($contract['contract_version'] ?? '1.1.0'),
        'lifecycle_status' => sanitize_key($contract['lifecycle_status'] ?? 'draft'),
        'save_state' => 'saved',
        'revision' => $revision,
        'content_hash' => $incoming_hash,
        'archived_at' => null,
        'created_at' => $existing ? $existing['created_at'] : $now,
        'updated_at' => $now,
        'contract_json' => wp_json_encode($contract, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
    );
    if ($existing) {
        $wpdb->update($table, $data, array('record_id' => $record_id));
        $action = 'save';
    } else {
        $wpdb->insert($table, $data);
        $action = 'create';
    }
    $wpdb->delete(gic_repository_table('autosaves'), array('initiative_id' => $data['initiative_id']));
    gic_repository_audit($action, $contract, $revision, array('content_hash' => $data['content_hash']));
    gic_evidence_materialize_contract($contract);
    gic_registry_materialize_contract($contract);
    gic_review_record_contract_revision($contract, $revision, $existing ? $existing['content_hash'] : '');
    return rest_ensure_response(array('contract' => $contract, 'repository' => array(
        'record_id' => $record_id, 'workspace_id' => $data['workspace_id'], 'initiative_id' => $data['initiative_id'],
        'revision' => $revision, 'content_hash' => $data['content_hash'], 'save_state' => 'saved', 'updated_at' => $now,
    )));
}

function gic_repository_autosave_contract(WP_REST_Request $request) {
    global $wpdb;
    $contract = $request->get_json_params();
    $valid = gic_repository_validate_contract($contract);
    if (is_wp_error($valid)) { return $valid; }
    $record_id = sanitize_text_field($contract['record_id']);
    $initiative_id = sanitize_text_field($contract['facts']['initiative']['id']);
    $base = (int) $request->get_param('base_revision');
    $actual = (int) $wpdb->get_var($wpdb->prepare("SELECT revision FROM " . gic_repository_table('contracts') . " WHERE record_id=%s", $record_id));
    if ($base !== $actual) {
        return new WP_Error('gic_revision_conflict', 'Autosave was rejected because the saved initiative changed.', array('status' => 409, 'expected_revision' => $base, 'actual_revision' => $actual));
    }
    $now = current_time('mysql', true);
    $data = array('initiative_id'=>$initiative_id,'record_id'=>$record_id,'base_revision'=>$base,'content_hash'=>gic_repository_hash($contract),'saved_at'=>$now,'contract_json'=>wp_json_encode($contract));
    $wpdb->replace(gic_repository_table('autosaves'), $data);
    gic_repository_audit('autosave', $contract, $base, array('content_hash'=>$data['content_hash']));
    return rest_ensure_response(array('initiative_id'=>$initiative_id,'base_revision'=>$base,'content_hash'=>$data['content_hash'],'saved_at'=>$now));
}

function gic_repository_list_contracts(WP_REST_Request $request) {
    global $wpdb;
    $table = gic_repository_table('contracts');
    $search = sanitize_text_field($request->get_param('search') ?? '');
    $include_archived = rest_sanitize_boolean($request->get_param('include_archived'));
    $where = $include_archived ? '1=1' : 'archived_at IS NULL';
    $params = array();
    if ($search !== '') {
        $where .= ' AND (initiative_name LIKE %s OR workspace_name LIKE %s)';
        $like = '%' . $wpdb->esc_like($search) . '%';
        $params = array($like, $like);
    }
    $sql = "SELECT record_id,workspace_id,initiative_id,workspace_name,initiative_name,lifecycle_status,revision,content_hash,archived_at,updated_at FROM {$table} WHERE {$where} ORDER BY updated_at DESC LIMIT 200";
    if ($params) { $sql = $wpdb->prepare($sql, $params); }
    return rest_ensure_response($wpdb->get_results($sql, ARRAY_A));
}

function gic_repository_get_contract(WP_REST_Request $request) {
    global $wpdb;
    $row = $wpdb->get_row($wpdb->prepare("SELECT * FROM " . gic_repository_table('contracts') . " WHERE record_id=%s", sanitize_text_field($request['record_id'])), ARRAY_A);
    if (!$row) { return new WP_Error('gic_not_found', 'Initiative not found.', array('status'=>404)); }
    $row['contract'] = json_decode($row['contract_json'], true);
    unset($row['contract_json']);
    $autosave = $wpdb->get_row($wpdb->prepare("SELECT * FROM " . gic_repository_table('autosaves') . " WHERE initiative_id=%s", $row['initiative_id']), ARRAY_A);
    if ($autosave) { $autosave['contract'] = json_decode($autosave['contract_json'], true); unset($autosave['contract_json']); }
    $row['autosave'] = $autosave;
    return rest_ensure_response($row);
}

function gic_repository_change_archive(WP_REST_Request $request) {
    global $wpdb;
    $table = gic_repository_table('contracts');
    $record_id = sanitize_text_field($request['record_id']);
    $row = $wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE record_id=%s", $record_id), ARRAY_A);
    if (!$row) { return new WP_Error('gic_not_found', 'Initiative not found.', array('status'=>404)); }
    $expected = (int) $request->get_param('expected_revision');
    if ($expected !== (int) $row['revision']) { return new WP_Error('gic_revision_conflict','Archive state changed in another session.',array('status'=>409,'actual_revision'=>(int)$row['revision'])); }
    $restore = rest_sanitize_boolean($request->get_param('restore'));
    $revision = (int) $row['revision'] + 1;
    $wpdb->update($table,array('archived_at'=>$restore?null:current_time('mysql',true),'revision'=>$revision,'updated_at'=>current_time('mysql',true)),array('record_id'=>$record_id));
    $contract = json_decode($row['contract_json'],true);
    gic_repository_audit($restore?'restore':'archive',$contract,$revision);
    return rest_ensure_response(array('record_id'=>$record_id,'revision'=>$revision,'archived'=>!$restore));
}

function gic_repository_register_routes() {
    register_rest_route('global-impact-catalyst/v1', '/records', array(
        array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_repository_list_contracts','permission_callback'=>'gic_repository_can_edit'),
        array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_repository_save_contract','permission_callback'=>'gic_repository_can_edit'),
    ));
    register_rest_route('global-impact-catalyst/v1', '/records/(?P<record_id>[A-Za-z0-9_-]+)', array(
        array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_repository_get_contract','permission_callback'=>'gic_repository_can_edit'),
        array('methods'=>WP_REST_Server::EDITABLE,'callback'=>'gic_repository_change_archive','permission_callback'=>'gic_repository_can_edit'),
    ));
    register_rest_route('global-impact-catalyst/v1', '/autosaves', array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_repository_autosave_contract','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init', 'gic_repository_register_routes');

function gic_workspace_shortcode($atts = array()) {
    if (!is_user_logged_in() || !current_user_can('edit_posts')) {
        return '<p class="gic-workspace__notice">Sign in with editing access to use the persistent impact workspace.</p>';
    }
    wp_enqueue_style('global-impact-catalyst-workspace');
    wp_enqueue_script('global-impact-catalyst-workspace');
    wp_localize_script('global-impact-catalyst-workspace', 'GlobalImpactCatalystWorkspaceConfig', array(
        'restUrl' => esc_url_raw(rest_url('global-impact-catalyst/v1/')),
        'nonce' => wp_create_nonce('wp_rest'),
        'version' => GIC_DEMO_VERSION,
    ));
    ob_start(); ?>
    <section class="gic-workspace" data-gic-workspace>
      <header class="gic-workspace__header">
        <p class="gic-demo__eyebrow">Persistent measurement repository · v1.3.0</p>
        <h2>Impact Workspace</h2>
        <p>Save, reopen, duplicate, search, archive, restore, import, and export canonical initiatives without changing calculation semantics.</p>
      </header>
      <div class="gic-workspace__toolbar">
        <label>Search initiatives <input type="search" data-gic-workspace-search placeholder="Initiative or workspace"></label>
        <label><input type="checkbox" data-gic-workspace-archived> Include archived</label>
        <button type="button" data-gic-workspace-refresh>Refresh</button>
        <button type="button" data-gic-workspace-new>New</button>
        <button type="button" data-gic-workspace-save>Save</button>
        <button type="button" data-gic-workspace-duplicate>Duplicate</button>
        <button type="button" data-gic-workspace-archive>Archive</button>
        <button type="button" data-gic-workspace-export>Export JSON</button>
        <label class="gic-workspace__import">Import JSON <input type="file" accept="application/json" data-gic-workspace-import></label>
      </div>
      <div class="gic-workspace__status" data-gic-workspace-status role="status" aria-live="polite">Repository ready.</div>
      <div class="gic-workspace__layout">
        <aside class="gic-workspace__library"><h3>Initiatives</h3><div data-gic-workspace-list></div></aside>
        <div class="gic-workspace__editor"><?php echo gic_demo_shortcode(); ?></div>
      </div>
    </section>
    <?php return ob_get_clean();
}
add_shortcode('global_impact_catalyst_workspace', 'gic_workspace_shortcode');


/** Sources, provenance, and evidence chain introduced in v1.3.0. */
function gic_evidence_id($kind, $parts) {
    return 'gic-' . sanitize_key($kind) . '-' . substr(hash('sha256', implode('|', array_map('strval', $parts))), 0, 20);
}

function gic_evidence_add_edge($workspace_id, $initiative_id, $subject_type, $subject_id, $predicate, $object_type, $object_id, $process_name = '', $method_id = '', $method_version = '') {
    global $wpdb;
    $edge_id = gic_evidence_id('edge', array($subject_type, $subject_id, $predicate, $object_type, $object_id, $method_id));
    $wpdb->replace(gic_repository_table('provenance'), array(
        'edge_id'=>$edge_id, 'workspace_id'=>$workspace_id, 'initiative_id'=>$initiative_id,
        'subject_type'=>$subject_type, 'subject_id'=>$subject_id, 'predicate'=>$predicate,
        'object_type'=>$object_type, 'object_id'=>$object_id, 'process_name'=>$process_name,
        'method_id'=>$method_id, 'method_version'=>$method_version,
        'occurred_at'=>current_time('mysql', true), 'actor'=>get_current_user_id(), 'metadata_json'=>'{}',
    ));
    return $edge_id;
}

function gic_evidence_materialize_contract($contract) {
    global $wpdb;
    $facts = $contract['facts'] ?? array();
    $workspace_id = sanitize_text_field($facts['workspace']['id'] ?? '');
    $initiative_id = sanitize_text_field($facts['initiative']['id'] ?? '');
    if (!$workspace_id || !$initiative_id) { return; }
    $methods = array();
    foreach (($facts['methods'] ?? array()) as $method) { $methods[$method['id']] = $method; }
    foreach (($facts['sources'] ?? array()) as $source) {
        $source_id = sanitize_text_field($source['id'] ?? '');
        if (!$source_id) { continue; }
        $now = current_time('mysql', true);
        $existing = $wpdb->get_row($wpdb->prepare('SELECT * FROM ' . gic_repository_table('sources') . ' WHERE source_id=%s', $source_id), ARRAY_A);
        $wpdb->replace(gic_repository_table('sources'), array(
            'source_id'=>$source_id, 'workspace_id'=>$workspace_id, 'initiative_id'=>$initiative_id,
            'title'=>sanitize_text_field($source['title'] ?? 'Untitled source'), 'source_type'=>sanitize_key($source['source_type'] ?? 'entered_source'),
            'locator'=>sanitize_text_field($source['locator'] ?? ''), 'url'=>'', 'doi'=>'', 'license'=>'not_recorded', 'access_rights'=>'not_recorded',
            'current_version'=>$existing ? (int)$existing['current_version'] : 0, 'revision'=>$existing ? (int)$existing['revision'] : 1,
            'created_at'=>$existing ? $existing['created_at'] : $now, 'updated_at'=>$now,
            'metadata_json'=>wp_json_encode(array('canonical_entity'=>$source), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
        ));
        $source_json = wp_json_encode($source, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        $checksum = hash('sha256', $source_json);
        $version = $wpdb->get_row($wpdb->prepare('SELECT * FROM ' . gic_repository_table('source_versions') . ' WHERE source_id=%s AND checksum_value=%s', $source_id, $checksum), ARRAY_A);
        if (!$version) {
            $number = 1 + (int)$wpdb->get_var($wpdb->prepare('SELECT COALESCE(MAX(version_number),0) FROM ' . gic_repository_table('source_versions') . ' WHERE source_id=%s', $source_id));
            $version_id = gic_evidence_id('source-version', array($source_id, $number, $checksum));
            $wpdb->insert(gic_repository_table('source_versions'), array(
                'source_version_id'=>$version_id, 'source_id'=>$source_id, 'version_number'=>$number,
                'version_label'=>'contract-' . sanitize_text_field($contract['contract_version'] ?? '1.1.0'),
                'content_hash'=>$checksum, 'checksum_algorithm'=>'sha256', 'checksum_value'=>$checksum,
                'mime_type'=>'application/vnd.global-impact-catalyst.source+json', 'size_bytes'=>strlen($source_json),
                'captured_at'=>$now, 'captured_by'=>get_current_user_id(), 'metadata_json'=>wp_json_encode(array('record_id'=>$contract['record_id'] ?? '')),
            ));
            $wpdb->update(gic_repository_table('sources'), array('current_version'=>$number), array('source_id'=>$source_id));
        }
    }
    $measurement = $facts['measurement'] ?? array();
    $records = array_filter(array_merge(array($measurement['baseline'] ?? null), $measurement['observations'] ?? array()));
    foreach ($records as $record) {
        $method_id = sanitize_text_field($record['method_id'] ?? '');
        $method = $methods[$method_id] ?? array();
        foreach (($record['source_ids'] ?? array()) as $source_id) {
            gic_evidence_add_edge($workspace_id, $initiative_id, 'source', sanitize_text_field($source_id), 'supports', sanitize_key($record['entity_type'] ?? 'measurement'), sanitize_text_field($record['id'] ?? ''), 'canonical contract materialization', $method_id, sanitize_text_field($method['version'] ?? ''));
        }
        if ($method_id) {
            gic_evidence_add_edge($workspace_id, $initiative_id, 'method', $method_id, 'produced', sanitize_key($record['entity_type'] ?? 'measurement'), sanitize_text_field($record['id'] ?? ''), sanitize_text_field($method['name'] ?? 'measurement method'), $method_id, sanitize_text_field($method['version'] ?? ''));
        }
    }
    foreach (($contract['derived']['claims'] ?? array()) as $claim) {
        foreach (($claim['evidence_refs'] ?? array()) as $reference) {
            $type = 'entity';
            foreach (array('source','method','baseline','observation','target') as $candidate) { if (strpos($reference, 'gic-' . $candidate . '-') === 0) { $type = $candidate; break; } }
            gic_evidence_add_edge($workspace_id, $initiative_id, $type, sanitize_text_field($reference), 'informs_claim', 'claim', sanitize_text_field($claim['id'] ?? ''), 'claim evidence declaration');
        }
    }
}

function gic_evidence_source_upsert(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $workspace_id = sanitize_text_field($data['workspace_id'] ?? '');
    $initiative_id = sanitize_text_field($data['initiative_id'] ?? '');
    $title = sanitize_text_field($data['title'] ?? '');
    if (!$workspace_id || !$title) { return new WP_Error('gic_evidence_invalid_source', 'Workspace and source title are required.', array('status'=>400)); }
    $source_id = sanitize_text_field($data['source_id'] ?? gic_evidence_id('source', array($workspace_id, $initiative_id, $title, $data['locator'] ?? '')));
    $existing = $wpdb->get_row($wpdb->prepare('SELECT * FROM ' . gic_repository_table('sources') . ' WHERE source_id=%s', $source_id), ARRAY_A);
    $now = current_time('mysql', true);
    $revision = $existing ? ((int)$existing['revision'] + 1) : 1;
    $row = array(
        'source_id'=>$source_id, 'workspace_id'=>$workspace_id, 'initiative_id'=>$initiative_id, 'title'=>$title,
        'source_type'=>sanitize_key($data['source_type'] ?? 'document'), 'locator'=>sanitize_text_field($data['locator'] ?? ''),
        'url'=>esc_url_raw($data['url'] ?? ''), 'doi'=>sanitize_text_field($data['doi'] ?? ''),
        'license'=>sanitize_text_field($data['license'] ?? 'not_recorded'), 'access_rights'=>sanitize_text_field($data['access_rights'] ?? 'not_recorded'),
        'current_version'=>$existing ? (int)$existing['current_version'] : 0, 'revision'=>$revision,
        'created_at'=>$existing ? $existing['created_at'] : $now, 'updated_at'=>$now, 'metadata_json'=>wp_json_encode($data['metadata'] ?? array()),
    );
    $wpdb->replace(gic_repository_table('sources'), $row);
    $checksum = hash('sha256', wp_json_encode($row));
    $version_id = gic_evidence_id('source-version', array($source_id, $revision, $checksum));
    $wpdb->replace(gic_repository_table('source_versions'), array(
        'source_version_id'=>$version_id, 'source_id'=>$source_id, 'version_number'=>$revision, 'version_label'=>'registry-' . $revision,
        'content_hash'=>$checksum, 'checksum_algorithm'=>'sha256', 'checksum_value'=>$checksum, 'mime_type'=>'application/json',
        'size_bytes'=>strlen(wp_json_encode($row)), 'captured_at'=>$now, 'captured_by'=>get_current_user_id(), 'metadata_json'=>'{}',
    ));
    $wpdb->update(gic_repository_table('sources'), array('current_version'=>$revision), array('source_id'=>$source_id));
    $row['current_version'] = $revision;
    return rest_ensure_response($row);
}

function gic_evidence_sources_list(WP_REST_Request $request) {
    global $wpdb;
    $initiative_id = sanitize_text_field($request->get_param('initiative_id') ?? '');
    $workspace_id = sanitize_text_field($request->get_param('workspace_id') ?? '');
    $where = array('1=1'); $params = array();
    if ($initiative_id) { $where[]='initiative_id=%s'; $params[]=$initiative_id; }
    if ($workspace_id) { $where[]='workspace_id=%s'; $params[]=$workspace_id; }
    $sql = 'SELECT * FROM ' . gic_repository_table('sources') . ' WHERE ' . implode(' AND ', $where) . ' ORDER BY updated_at DESC LIMIT 200';
    if ($params) { $sql = $wpdb->prepare($sql, $params); }
    return rest_ensure_response($wpdb->get_results($sql, ARRAY_A));
}

function gic_evidence_capture_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $source_id = sanitize_text_field($data['source_id'] ?? '');
    $source = $wpdb->get_row($wpdb->prepare('SELECT * FROM ' . gic_repository_table('sources') . ' WHERE source_id=%s', $source_id), ARRAY_A);
    if (!$source) { return new WP_Error('gic_evidence_source_missing', 'Source not found.', array('status'=>404)); }
    $quote = sanitize_textarea_field($data['exact_quote'] ?? ''); $paraphrase = sanitize_textarea_field($data['paraphrase'] ?? ''); $notes = sanitize_textarea_field($data['notes'] ?? '');
    if (!$quote && !$paraphrase && !$notes) { return new WP_Error('gic_evidence_empty', 'Evidence requires a quotation, paraphrase, or note.', array('status'=>400)); }
    $payload = array('source_id'=>$source_id,'locator'=>$data['locator'] ?? '','exact_quote'=>$quote,'paraphrase'=>$paraphrase,'notes'=>$notes);
    $hash = hash('sha256', wp_json_encode($payload));
    $evidence_id = sanitize_text_field($data['evidence_id'] ?? gic_evidence_id('evidence', array($source_id, $hash)));
    $version_id = (string)$wpdb->get_var($wpdb->prepare('SELECT source_version_id FROM ' . gic_repository_table('source_versions') . ' WHERE source_id=%s ORDER BY version_number DESC LIMIT 1', $source_id));
    $row = array(
        'evidence_id'=>$evidence_id, 'source_id'=>$source_id, 'source_version_id'=>$version_id,
        'workspace_id'=>$source['workspace_id'], 'initiative_id'=>$source['initiative_id'],
        'evidence_type'=>sanitize_key($data['evidence_type'] ?? 'excerpt'), 'title'=>sanitize_text_field($data['title'] ?? ''),
        'locator'=>sanitize_text_field($data['locator'] ?? ''), 'exact_quote'=>$quote, 'paraphrase'=>$paraphrase, 'notes'=>$notes,
        'content_hash'=>$hash, 'captured_at'=>current_time('mysql', true), 'captured_by'=>get_current_user_id(),
        'metadata_json'=>wp_json_encode($data['metadata'] ?? array()),
    );
    $wpdb->replace(gic_repository_table('evidence'), $row);
    return rest_ensure_response($row);
}

function gic_evidence_dataset_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $source_id = sanitize_text_field($data['source_id'] ?? '');
    $source = $wpdb->get_row($wpdb->prepare('SELECT * FROM ' . gic_repository_table('sources') . ' WHERE source_id=%s', $source_id), ARRAY_A);
    if (!$source || empty($data['title'])) { return new WP_Error('gic_dataset_invalid', 'A valid source and dataset title are required.', array('status'=>400)); }
    $checksum = strtolower(sanitize_text_field($data['checksum_value'] ?? hash('sha256', wp_json_encode($data))));
    if (!preg_match('/^[a-f0-9]{64}$/', $checksum)) { return new WP_Error('gic_dataset_checksum', 'Dataset checksum must be a SHA-256 value.', array('status'=>400)); }
    $dataset_id = sanitize_text_field($data['dataset_id'] ?? gic_evidence_id('dataset', array($source_id, $data['title'], $data['version'] ?? '', $checksum)));
    $now = current_time('mysql', true);
    $row = array(
        'dataset_id'=>$dataset_id,'source_id'=>$source_id,'workspace_id'=>$source['workspace_id'],'initiative_id'=>$source['initiative_id'],
        'title'=>sanitize_text_field($data['title']),'version'=>sanitize_text_field($data['version'] ?? ''),'license'=>sanitize_text_field($data['license'] ?? $source['license']),
        'checksum_algorithm'=>'sha256','checksum_value'=>$checksum,'schema_fingerprint'=>sanitize_text_field($data['schema_fingerprint'] ?? ''),
        'temporal_coverage'=>sanitize_text_field($data['temporal_coverage'] ?? ''),'spatial_coverage'=>sanitize_text_field($data['spatial_coverage'] ?? ''),
        'row_count'=>isset($data['row_count'])?(int)$data['row_count']:null,'column_count'=>isset($data['column_count'])?(int)$data['column_count']:null,
        'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata'] ?? array()),
    );
    $wpdb->replace(gic_repository_table('datasets'), $row);
    return rest_ensure_response($row);
}

function gic_evidence_link_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $claim_id = sanitize_text_field($data['claim_id'] ?? ''); $evidence_id = sanitize_text_field($data['evidence_id'] ?? '');
    $relationships = array('supports','contradicts','qualifies','context'); $strengths = array('direct','indirect','contextual');
    $relationship = sanitize_key($data['relationship'] ?? 'supports'); $strength = sanitize_key($data['strength'] ?? 'direct');
    if (!$claim_id || !$evidence_id || !in_array($relationship,$relationships,true) || !in_array($strength,$strengths,true)) { return new WP_Error('gic_claim_evidence_invalid','Claim, evidence, relationship, and strength are required.',array('status'=>400)); }
    $row = array('claim_id'=>$claim_id,'evidence_id'=>$evidence_id,'relationship'=>$relationship,'strength'=>$strength,'notes'=>sanitize_textarea_field($data['notes'] ?? ''),'linked_at'=>current_time('mysql',true),'linked_by'=>get_current_user_id());
    $wpdb->replace(gic_repository_table('claim_evidence'),$row);
    return rest_ensure_response($row);
}

function gic_evidence_chain_rest(WP_REST_Request $request) {
    global $wpdb;
    $initiative_id = sanitize_text_field($request['initiative_id']);
    $contract_row = $wpdb->get_row($wpdb->prepare('SELECT workspace_id, contract_json FROM ' . gic_repository_table('contracts') . ' WHERE initiative_id=%s', $initiative_id), ARRAY_A);
    if (!$contract_row) { return new WP_Error('gic_evidence_initiative_missing', 'Initiative not found.', array('status'=>404)); }
    $workspace_id = sanitize_text_field($contract_row['workspace_id']);
    $contract = json_decode($contract_row['contract_json'], true);
    $claim_ids = array();
    foreach (($contract['derived']['claims'] ?? array()) as $claim) { if (!empty($claim['id'])) { $claim_ids[(string)$claim['id']] = true; } }
    $sources = $wpdb->get_results($wpdb->prepare('SELECT * FROM ' . gic_repository_table('sources') . ' WHERE initiative_id=%s ORDER BY title', $initiative_id), ARRAY_A);
    foreach ($sources as &$source) {
        $source['metadata'] = json_decode($source['metadata_json'] ?? '{}', true) ?: array(); unset($source['metadata_json']);
        $versions = $wpdb->get_results($wpdb->prepare('SELECT * FROM ' . gic_repository_table('source_versions') . ' WHERE source_id=%s ORDER BY version_number', $source['source_id']), ARRAY_A);
        foreach ($versions as &$version) { $version['metadata'] = json_decode($version['metadata_json'] ?? '{}', true) ?: array(); unset($version['metadata_json']); }
        unset($version); $source['versions'] = $versions;
    }
    unset($source);
    $evidence = $wpdb->get_results($wpdb->prepare('SELECT * FROM ' . gic_repository_table('evidence') . ' WHERE initiative_id=%s ORDER BY captured_at', $initiative_id), ARRAY_A);
    foreach ($evidence as &$item) { $item['metadata'] = json_decode($item['metadata_json'] ?? '{}', true) ?: array(); unset($item['metadata_json']); }
    unset($item);
    $datasets = $wpdb->get_results($wpdb->prepare('SELECT * FROM ' . gic_repository_table('datasets') . ' WHERE initiative_id=%s ORDER BY title', $initiative_id), ARRAY_A);
    foreach ($datasets as &$dataset) { $dataset['metadata'] = json_decode($dataset['metadata_json'] ?? '{}', true) ?: array(); unset($dataset['metadata_json']); }
    unset($dataset);
    $edges = $wpdb->get_results($wpdb->prepare('SELECT * FROM ' . gic_repository_table('provenance') . ' WHERE initiative_id=%s ORDER BY occurred_at,edge_id', $initiative_id), ARRAY_A);
    foreach ($edges as &$edge) { $edge['metadata'] = json_decode($edge['metadata_json'] ?? '{}', true) ?: array(); unset($edge['metadata_json']); }
    unset($edge);
    $links = $wpdb->get_results($wpdb->prepare('SELECT l.* FROM ' . gic_repository_table('claim_evidence') . ' l INNER JOIN ' . gic_repository_table('evidence') . ' e ON e.evidence_id=l.evidence_id WHERE e.initiative_id=%s ORDER BY l.linked_at', $initiative_id), ARRAY_A);
    $evidence_ids = array(); foreach ($evidence as $item) { $evidence_ids[(string)$item['evidence_id']] = true; }
    $missing = array(); $version_count = 0;
    foreach ($sources as $source) { $version_count += count($source['versions']); if (empty($source['versions'])) { $missing[]=$source['source_id']; } }
    $orphans = array(); foreach ($links as $link) { if (empty($evidence_ids[(string)$link['evidence_id']]) || empty($claim_ids[(string)$link['claim_id']])) { $orphans[] = $link; } }
    $contradictions = array_filter($links, static function($link){ return $link['relationship']==='contradicts'; });
    return rest_ensure_response(array(
        'chain_type'=>'global_impact_evidence_chain','chain_version'=>'1.3.0','workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,'generated_at'=>gmdate('c'),
        'sources'=>$sources,'evidence_items'=>$evidence,'datasets'=>$datasets,'provenance_edges'=>$edges,'claim_evidence_links'=>$links,
        'integrity'=>array('valid'=>empty($missing) && empty($orphans),'source_count'=>count($sources),'version_count'=>$version_count,'evidence_count'=>count($evidence),'dataset_count'=>count($datasets),'edge_count'=>count($edges),'claim_link_count'=>count($links),'missing_checksum_source_ids'=>$missing,'orphan_claim_evidence_links'=>$orphans,'contradicting_link_count'=>count($contradictions)),
    ));
}

function gic_evidence_register_routes() {
    register_rest_route('global-impact-catalyst/v1','/sources',array(
        array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_evidence_sources_list','permission_callback'=>'gic_repository_can_edit'),
        array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_evidence_source_upsert','permission_callback'=>'gic_repository_can_edit'),
    ));
    register_rest_route('global-impact-catalyst/v1','/evidence',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_evidence_capture_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/datasets',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_evidence_dataset_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/claim-evidence',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_evidence_link_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/evidence-chain/(?P<initiative_id>[A-Za-z0-9_-]+)',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_evidence_chain_rest','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init','gic_evidence_register_routes');

function gic_evidence_ledger_shortcode($atts = array()) {
    if (!is_user_logged_in() || !current_user_can('edit_posts')) { return '<p class="gic-evidence__notice">Sign in with editing access to use the evidence ledger.</p>'; }
    static $instance = 0; $instance++; $prefix = 'gic-evidence-' . $instance . '-' . wp_rand(1000,999999);
    wp_enqueue_style('global-impact-catalyst-evidence'); wp_enqueue_script('global-impact-catalyst-evidence');
    wp_localize_script('global-impact-catalyst-evidence','GlobalImpactCatalystEvidenceConfig',array('restUrl'=>esc_url_raw(rest_url('global-impact-catalyst/v1/')),'nonce'=>wp_create_nonce('wp_rest'),'version'=>GIC_DEMO_VERSION));
    ob_start(); ?>
    <section class="gic-evidence" data-gic-evidence-ledger>
      <header><p class="gic-demo__eyebrow">Sources, provenance, and evidence chain · v1.3.0</p><h2>Impact Evidence Ledger</h2><p>Register sources, preserve versions and checksums, capture excerpts, describe datasets, and inspect the chain supporting or challenging impact claims.</p></header>
      <div class="gic-evidence__toolbar">
        <label for="<?php echo esc_attr($prefix.'-initiative'); ?>">Initiative ID</label>
        <input id="<?php echo esc_attr($prefix.'-initiative'); ?>" type="text" data-gic-evidence-initiative placeholder="gic-initiative-…">
        <button type="button" data-gic-evidence-load>Load chain</button>
        <button type="button" data-gic-evidence-download>Export chain</button>
      </div>
      <div class="gic-evidence__status" data-gic-evidence-status role="status" aria-live="polite">Evidence repository ready.</div>
      <div class="gic-evidence__grid">
        <form data-gic-source-form><h3>Register source</h3><input name="workspace_id" placeholder="Workspace ID" required><input name="initiative_id" placeholder="Initiative ID"><input name="title" placeholder="Source title" required><input name="locator" placeholder="Locator or citation"><input name="url" placeholder="URL"><input name="doi" placeholder="DOI"><input name="license" placeholder="License" value="not_recorded"><button type="submit">Save source</button></form>
        <form data-gic-evidence-form><h3>Capture evidence</h3><input name="source_id" placeholder="Source ID" required><select name="evidence_type"><option value="quotation">Quotation</option><option value="excerpt">Excerpt</option><option value="document_note">Document note</option><option value="observation_note">Observation note</option><option value="table">Table</option><option value="figure">Figure</option></select><input name="title" placeholder="Evidence title"><input name="locator" placeholder="Page, table, or section"><textarea name="exact_quote" placeholder="Exact quotation"></textarea><textarea name="paraphrase" placeholder="Paraphrase"></textarea><textarea name="notes" placeholder="Notes"></textarea><button type="submit">Capture evidence</button></form>
        <form data-gic-dataset-form><h3>Register dataset</h3><input name="source_id" placeholder="Source ID" required><input name="title" placeholder="Dataset title" required><input name="version" placeholder="Version"><input name="license" placeholder="License"><input name="checksum_value" placeholder="SHA-256 checksum"><input name="schema_fingerprint" placeholder="Schema fingerprint"><button type="submit">Save dataset</button></form>
        <form data-gic-claim-link-form><h3>Link evidence to claim</h3><input name="claim_id" placeholder="Claim ID" required><input name="evidence_id" placeholder="Evidence ID" required><select name="relationship"><option value="supports">Supports</option><option value="contradicts">Contradicts</option><option value="qualifies">Qualifies</option><option value="context">Context</option></select><select name="strength"><option value="direct">Direct</option><option value="indirect">Indirect</option><option value="contextual">Contextual</option></select><textarea name="notes" placeholder="Link notes"></textarea><button type="submit">Link evidence</button></form>
      </div>
      <div class="gic-evidence__summary" data-gic-evidence-summary></div>
      <div class="gic-evidence__records" data-gic-evidence-records></div>
    </section>
    <?php return ob_get_clean();
}
add_shortcode('global_impact_catalyst_evidence_ledger','gic_evidence_ledger_shortcode');

/** Indicator Registry, Units, Baselines, Targets, and Methods — v1.4.0. */
function gic_registry_id($kind, $parts) {
    return 'gic-' . sanitize_key($kind) . '-' . substr(hash('sha256', implode('|', array_map('strval', (array) $parts))), 0, 20);
}

function gic_registry_seed_units() {
    global $wpdb;
    $now = current_time('mysql', true);
    $units = array(
        array('gic-unit-ratio','ratio','','Ratio','dimensionless','gic-unit-ratio',1,0,4),
        array('gic-unit-percent','%','%','Percent','dimensionless','gic-unit-ratio',0.01,0,2),
        array('gic-unit-count','count','','Count','count','gic-unit-count',1,0,0),
        array('gic-unit-usd','USD','$','US dollar','currency_usd','gic-unit-usd',1,0,2),
        array('gic-unit-kwh','kWh','kWh','Kilowatt hour','energy','gic-unit-kwh',1,0,3),
        array('gic-unit-mwh','MWh','MWh','Megawatt hour','energy','gic-unit-kwh',1000,0,3),
        array('gic-unit-kg','kg','kg','Kilogram','mass','gic-unit-kg',1,0,3),
        array('gic-unit-tonne','t','t','Metric tonne','mass','gic-unit-kg',1000,0,3),
        array('gic-unit-kgco2e','kgCO2e','kgCO2e','Kilogram CO2 equivalent','emissions','gic-unit-kgco2e',1,0,3),
        array('gic-unit-tco2e','tCO2e','tCO2e','Metric tonne CO2 equivalent','emissions','gic-unit-kgco2e',1000,0,3),
        array('gic-unit-metre','m','m','Metre','length','gic-unit-metre',1,0,3),
        array('gic-unit-kilometre','km','km','Kilometre','length','gic-unit-metre',1000,0,3),
        array('gic-unit-square-metre','m2','m2','Square metre','area','gic-unit-square-metre',1,0,3),
        array('gic-unit-hectare','ha','ha','Hectare','area','gic-unit-square-metre',10000,0,3),
        array('gic-unit-litre','L','L','Litre','volume','gic-unit-litre',1,0,3),
        array('gic-unit-cubic-metre','m3','m3','Cubic metre','volume','gic-unit-litre',1000,0,3),
        array('gic-unit-hour','hour','h','Hour','time','gic-unit-hour',1,0,2),
        array('gic-unit-day','day','d','Day','time','gic-unit-hour',24,0,2),
    );
    foreach ($units as $unit) {
        $wpdb->replace(gic_repository_table('units'), array(
            'unit_id'=>$unit[0], 'workspace_id'=>'', 'code'=>$unit[1], 'symbol'=>$unit[2], 'name'=>$unit[3],
            'dimension'=>$unit[4], 'canonical_unit_id'=>$unit[5], 'scale_to_canonical'=>$unit[6],
            'offset_to_canonical'=>$unit[7], 'precision_digits'=>$unit[8], 'lifecycle_status'=>'active',
            'revision'=>1, 'created_at'=>$now, 'updated_at'=>$now,
            'metadata_json'=>wp_json_encode(array('standard'=>true,'registry_version'=>'1.4.0')),
        ));
    }
}

function gic_registry_unit_by_code($code, $workspace_id = '') {
    global $wpdb;
    $table = gic_repository_table('units');
    return $wpdb->get_row($wpdb->prepare(
        "SELECT * FROM {$table} WHERE LOWER(code)=LOWER(%s) AND (workspace_id=%s OR workspace_id='') ORDER BY workspace_id DESC LIMIT 1",
        sanitize_text_field($code), sanitize_text_field($workspace_id)
    ), ARRAY_A);
}

function gic_registry_store_version($kind, $entity_id, $document, $label = '1.0') {
    global $wpdb;
    $map = array(
        'indicator'=>array('indicator_versions','indicator_definition_id','indicator_definition_version_id','definition_hash','definition_json'),
        'baseline'=>array('baseline_versions','baseline_model_id','baseline_model_version_id','model_hash','model_json'),
        'target'=>array('target_versions','target_model_id','target_model_version_id','model_hash','model_json'),
        'method'=>array('method_versions','method_definition_id','method_definition_version_id','method_hash','method_json'),
    );
    if (!isset($map[$kind])) { return array(); }
    list($suffix,$entity_field,$version_field,$hash_field,$json_field) = $map[$kind];
    $table = gic_repository_table($suffix);
    $json = wp_json_encode($document, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    $hash = hash('sha256', $json);
    $existing = $wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE {$entity_field}=%s AND {$hash_field}=%s", $entity_id, $hash), ARRAY_A);
    if ($existing) { return $existing; }
    $number = (int) $wpdb->get_var($wpdb->prepare("SELECT COALESCE(MAX(version_number),0)+1 FROM {$table} WHERE {$entity_field}=%s", $entity_id));
    $version_id = gic_registry_id($kind . '-version', array($entity_id,$number,$hash));
    $wpdb->insert($table, array(
        $version_field=>$version_id, $entity_field=>$entity_id, 'version_number'=>$number,
        'version_label'=>sanitize_text_field($label ?: (string) $number), $hash_field=>$hash,
        $json_field=>$json, 'created_at'=>current_time('mysql', true), 'created_by'=>get_current_user_id(),
    ));
    return $wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE {$version_field}=%s", $version_id), ARRAY_A);
}

function gic_registry_materialize_contract($contract) {
    global $wpdb;
    if (empty($contract['facts']['indicator']) || empty($contract['facts']['measurement'])) { return; }
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_benchmarks') . " (benchmark_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, indicator_id varchar(96) NOT NULL, name text NOT NULL, value decimal(30,10) NOT NULL, unit_id varchar(96) NOT NULL, period_label varchar(160) NOT NULL DEFAULT '', geography text NOT NULL, population text NOT NULL, quality_status varchar(32) NOT NULL DEFAULT 'not_assessed', revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (benchmark_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_comparison_sets') . " (comparison_set_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, indicator_id varchar(96) NOT NULL, name text NOT NULL, policy_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (comparison_set_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_comparison_members') . " (comparison_member_id varchar(96) NOT NULL, comparison_set_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', benchmark_id varchar(96) NOT NULL DEFAULT '', label text NOT NULL, value_override decimal(30,10) NULL, unit_id varchar(96) NOT NULL DEFAULT '', metadata_json longtext NOT NULL, PRIMARY KEY (comparison_member_id), KEY comparison_set_id (comparison_set_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_scenarios') . " (scenario_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL, indicator_id varchar(96) NOT NULL, name text NOT NULL, model_type varchar(32) NOT NULL, periods int unsigned NOT NULL DEFAULT 1, base_value decimal(30,10) NULL, unit_id varchar(96) NOT NULL, parameters_json longtext NOT NULL, assumptions_json longtext NOT NULL, limitations_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (scenario_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_uncertainty_models') . " (uncertainty_model_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, name text NOT NULL, uncertainty_type varchar(32) NOT NULL, absolute_margin decimal(30,10) NULL, relative_margin_percent decimal(20,8) NULL, lower_bound decimal(30,10) NULL, upper_bound decimal(30,10) NULL, confidence_level decimal(8,6) NOT NULL DEFAULT .95, distribution varchar(48) NOT NULL DEFAULT 'bounded', assumptions_json longtext NOT NULL, limitations_json longtext NOT NULL, revision bigint unsigned NOT NULL DEFAULT 1, created_at datetime NOT NULL, updated_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (uncertainty_model_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_runs') . " (analysis_run_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL DEFAULT '', analysis_type varchar(48) NOT NULL, subject_id varchar(96) NOT NULL, input_hash char(64) NOT NULL, result_hash char(64) NOT NULL, result_json longtext NOT NULL, created_by varchar(190) NOT NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (analysis_run_id), KEY workspace_id (workspace_id)) {$charset};");
    dbDelta("CREATE TABLE " . gic_repository_table('analysis_sensitivity_runs') . " (sensitivity_run_id varchar(96) NOT NULL, scenario_id varchar(96) NOT NULL, workspace_id varchar(96) NOT NULL, initiative_id varchar(96) NOT NULL, parameter_name varchar(120) NOT NULL, absolute_effect decimal(30,10) NOT NULL, rank_order int unsigned NOT NULL, created_at datetime NOT NULL, metadata_json longtext NOT NULL, PRIMARY KEY (sensitivity_run_id), KEY workspace_id (workspace_id)) {$charset};");
    gic_registry_seed_units();
    $workspace_id = sanitize_text_field($contract['facts']['workspace']['id'] ?? '');
    $initiative_id = sanitize_text_field($contract['facts']['initiative']['id'] ?? '');
    $indicator = $contract['facts']['indicator'];
    $definition = $indicator['definition_version'] ?? array();
    $measurement = $contract['facts']['measurement'];
    $unit_code = sanitize_text_field($definition['unit'] ?? ($measurement['baseline']['unit'] ?? 'count'));
    $unit = gic_registry_unit_by_code($unit_code, $workspace_id);
    if (!$unit) {
        $unit_id = gic_registry_id('unit', array($workspace_id,strtolower($unit_code)));
        $now = current_time('mysql', true);
        $wpdb->replace(gic_repository_table('units'), array(
            'unit_id'=>$unit_id,'workspace_id'=>$workspace_id,'code'=>$unit_code,'symbol'=>$unit_code,'name'=>$unit_code,
            'dimension'=>'custom','canonical_unit_id'=>$unit_id,'scale_to_canonical'=>1,'offset_to_canonical'=>0,
            'precision_digits'=>2,'lifecycle_status'=>'active','revision'=>1,'created_at'=>$now,'updated_at'=>$now,
            'metadata_json'=>wp_json_encode(array('materialized_from_contract'=>$contract['record_id'] ?? '')),
        ));
        $unit = gic_registry_unit_by_code($unit_code, $workspace_id);
    }
    $now = current_time('mysql', true);
    $indicator_definition_id = gic_registry_id('indicator-definition', array($workspace_id,strtolower($indicator['name'] ?? 'indicator')));
    $indicator_doc = array(
        'indicator_definition_id'=>$indicator_definition_id,'workspace_id'=>$workspace_id,
        'name'=>sanitize_text_field($indicator['name'] ?? 'Indicator'),'description'=>sanitize_textarea_field($definition['name'] ?? ''),
        'direction'=>sanitize_key($definition['direction'] ?? 'higher_is_better'),'unit_id'=>$unit['unit_id'],
        'aggregation_method'=>'latest','formula_expression'=>'','formula_language'=>'gic-expression-1.0',
        'disaggregation'=>array(),'quality_profile'=>array('status'=>'not_assessed'),
        'lifecycle_status'=>'active','metadata'=>array('canonical_indicator_id'=>$indicator['id'] ?? '','record_id'=>$contract['record_id'] ?? ''),
    );
    $existing = $wpdb->get_row($wpdb->prepare("SELECT revision,created_at FROM " . gic_repository_table('indicator_definitions') . " WHERE indicator_definition_id=%s", $indicator_definition_id), ARRAY_A);
    $version = gic_registry_store_version('indicator',$indicator_definition_id,$indicator_doc,$definition['version'] ?? '1.0');
    $wpdb->replace(gic_repository_table('indicator_definitions'), array(
        'indicator_definition_id'=>$indicator_definition_id,'workspace_id'=>$workspace_id,'name'=>$indicator_doc['name'],
        'description'=>$indicator_doc['description'],'direction'=>$indicator_doc['direction'],'unit_id'=>$unit['unit_id'],
        'aggregation_method'=>'latest','formula_expression'=>'','formula_language'=>'gic-expression-1.0',
        'disaggregation_json'=>'[]','quality_profile_json'=>wp_json_encode($indicator_doc['quality_profile']),
        'lifecycle_status'=>'active','current_version'=>(int) ($version['version_number'] ?? 1),
        'revision'=>$existing ? ((int) $existing['revision'] + 1) : 1,'created_at'=>$existing['created_at'] ?? $now,'updated_at'=>$now,
        'metadata_json'=>wp_json_encode($indicator_doc['metadata']),
    ));

    $baseline = $measurement['baseline'] ?? array();
    $baseline_id = gic_registry_id('baseline-model', array($workspace_id,$indicator['id'] ?? ''));
    $baseline_doc = array('baseline_model_id'=>$baseline_id,'workspace_id'=>$workspace_id,'name'=>($indicator_doc['name'] . ' entered baseline'),'method_type'=>'benchmark','unit_id'=>$unit['unit_id'],'benchmark_value'=>(float) ($baseline['value'] ?? 0),'minimum_observations'=>1,'confidence'=>'medium','parameters'=>array('canonical_baseline_id'=>$baseline['id'] ?? ''),'metadata'=>array('record_id'=>$contract['record_id'] ?? ''));
    $baseline_version = gic_registry_store_version('baseline',$baseline_id,$baseline_doc,$contract['contract_version'] ?? '1.1.0');
    $wpdb->replace(gic_repository_table('baseline_models'), array(
        'baseline_model_id'=>$baseline_id,'workspace_id'=>$workspace_id,'name'=>$baseline_doc['name'],'method_type'=>'benchmark',
        'unit_id'=>$unit['unit_id'],'description'=>'Entered canonical baseline','benchmark_value'=>$baseline_doc['benchmark_value'],
        'rolling_periods'=>null,'formula_expression'=>'','minimum_observations'=>1,'confidence'=>'medium',
        'parameters_json'=>wp_json_encode($baseline_doc['parameters']),'lifecycle_status'=>'active','current_version'=>(int) ($baseline_version['version_number'] ?? 1),
        'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($baseline_doc['metadata']),
    ));

    $target = $measurement['target'] ?? array();
    $target_id = gic_registry_id('target-model', array($workspace_id,$indicator['id'] ?? ''));
    $target_doc = array('target_model_id'=>$target_id,'workspace_id'=>$workspace_id,'indicator_definition_id'=>$indicator_definition_id,'name'=>($indicator_doc['name'] . ' target'),'target_type'=>'absolute','unit_id'=>$unit['unit_id'],'direction'=>sanitize_key($target['direction'] ?? $indicator_doc['direction']),'target_value'=>(float) ($target['value'] ?? 0),'end_period'=>sanitize_text_field($target['period']['label'] ?? ''),'trajectory_type'=>'linear','milestones'=>array(),'metadata'=>array('canonical_target_id'=>$target['id'] ?? '','record_id'=>$contract['record_id'] ?? ''));
    $target_version = gic_registry_store_version('target',$target_id,$target_doc,$contract['contract_version'] ?? '1.1.0');
    $wpdb->replace(gic_repository_table('target_models'), array(
        'target_model_id'=>$target_id,'workspace_id'=>$workspace_id,'indicator_definition_id'=>$indicator_definition_id,
        'name'=>$target_doc['name'],'target_type'=>'absolute','unit_id'=>$unit['unit_id'],'direction'=>$target_doc['direction'],
        'target_value'=>$target_doc['target_value'],'lower_value'=>null,'upper_value'=>null,'relative_change_percent'=>null,
        'start_period'=>'','end_period'=>$target_doc['end_period'],'start_value'=>null,'end_value'=>null,
        'trajectory_type'=>'linear','formula_expression'=>'','milestones_json'=>'[]','lifecycle_status'=>'active',
        'current_version'=>(int) ($target_version['version_number'] ?? 1),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,
        'metadata_json'=>wp_json_encode($target_doc['metadata']),
    ));

    $method = $contract['facts']['methods'][0] ?? array();
    $method_id = sanitize_text_field($method['id'] ?? gic_registry_id('method-definition',array($workspace_id,'entered-method')));
    $method_doc = array('method_definition_id'=>$method_id,'workspace_id'=>$workspace_id,'name'=>sanitize_text_field($method['name'] ?? 'Entered measurement method'),'method_kind'=>'measurement','design_type'=>sanitize_key($method['design_type'] ?? 'monitoring'),'description'=>sanitize_textarea_field($method['description'] ?? ''),'formula_expression'=>'','input_requirements'=>array(),'quality_profile'=>array('reproducibility'=>strlen((string) ($method['description'] ?? '')) >= 80 ? 'documented' : 'partial','data_quality'=>'not_assessed','review_status'=>sanitize_key($contract['lifecycle_status'] ?? 'draft')),'limitations'=>array(),'metadata'=>array('record_id'=>$contract['record_id'] ?? ''));
    $method_version = gic_registry_store_version('method',$method_id,$method_doc,$method['version'] ?? '1.0');
    $wpdb->replace(gic_repository_table('method_definitions'), array(
        'method_definition_id'=>$method_id,'workspace_id'=>$workspace_id,'name'=>$method_doc['name'],'method_kind'=>'measurement',
        'design_type'=>$method_doc['design_type'],'description'=>$method_doc['description'],'formula_expression'=>'',
        'input_requirements_json'=>'[]','quality_profile_json'=>wp_json_encode($method_doc['quality_profile']),
        'limitations_json'=>'[]','lifecycle_status'=>'active','current_version'=>(int) ($method_version['version_number'] ?? 1),
        'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($method_doc['metadata']),
    ));

    $binding_id = gic_registry_id('indicator-binding',array($initiative_id,$indicator['id'] ?? ''));
    $wpdb->replace(gic_repository_table('indicator_bindings'), array(
        'binding_id'=>$binding_id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,
        'indicator_id'=>sanitize_text_field($indicator['id'] ?? ''),'indicator_definition_id'=>$indicator_definition_id,
        'indicator_definition_version_id'=>$version['indicator_definition_version_id'] ?? '', 'unit_id'=>$unit['unit_id'],
        'baseline_model_id'=>$baseline_id,'baseline_model_version_id'=>$baseline_version['baseline_model_version_id'] ?? '',
        'target_model_id'=>$target_id,'target_model_version_id'=>$target_version['target_model_version_id'] ?? '',
        'method_definition_id'=>$method_id,'method_definition_version_id'=>$method_version['method_definition_version_id'] ?? '',
        'bound_at'=>$now,'bound_by'=>get_current_user_id(),'revision'=>1,
        'metadata_json'=>wp_json_encode(array('materialized_from_contract'=>$contract['record_id'] ?? '')),
    ));
}

function gic_registry_decode_rows($table, $workspace_id, $json_fields = array()) {
    global $wpdb;
    $rows = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$table} WHERE workspace_id=%s ORDER BY name", $workspace_id), ARRAY_A);
    foreach ($rows as &$row) {
        foreach ($json_fields as $field) {
            $row[preg_replace('/_json$/','',$field)] = json_decode($row[$field] ?? '', true) ?: array();
            unset($row[$field]);
        }
    }
    return $rows;
}

function gic_registry_export($workspace_id) {
    global $wpdb;
    $workspace_id = sanitize_text_field($workspace_id);
    $units_table = gic_repository_table('units');
    $units = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$units_table} WHERE workspace_id='' OR workspace_id=%s ORDER BY dimension,code", $workspace_id), ARRAY_A);
    foreach ($units as &$unit) { $unit['metadata'] = json_decode($unit['metadata_json'] ?? '', true) ?: array(); unset($unit['metadata_json']); }
    $indicators = gic_registry_decode_rows(gic_repository_table('indicator_definitions'),$workspace_id,array('disaggregation_json','quality_profile_json','metadata_json'));
    $baselines = gic_registry_decode_rows(gic_repository_table('baseline_models'),$workspace_id,array('parameters_json','metadata_json'));
    $targets = gic_registry_decode_rows(gic_repository_table('target_models'),$workspace_id,array('milestones_json','metadata_json'));
    $methods = gic_registry_decode_rows(gic_repository_table('method_definitions'),$workspace_id,array('input_requirements_json','quality_profile_json','limitations_json','metadata_json'));
    $bindings_table = gic_repository_table('indicator_bindings');
    $bindings = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$bindings_table} WHERE workspace_id=%s ORDER BY initiative_id,indicator_id", $workspace_id), ARRAY_A);
    foreach ($bindings as &$binding) { $binding['metadata'] = json_decode($binding['metadata_json'] ?? '', true) ?: array(); unset($binding['metadata_json']); }
    return array(
        'registry_type'=>'global_impact_indicator_registry','registry_version'=>'1.4.0','workspace_id'=>$workspace_id,
        'generated_at'=>gmdate('c'),'units'=>$units,'indicator_definitions'=>$indicators,'baseline_models'=>$baselines,
        'target_models'=>$targets,'method_definitions'=>$methods,'bindings'=>$bindings,
        'integrity'=>array('valid'=>true,'unit_count'=>count($units),'indicator_definition_count'=>count($indicators),
            'baseline_model_count'=>count($baselines),'target_model_count'=>count($targets),
            'method_definition_count'=>count($methods),'binding_count'=>count($bindings),
            'missing_unit_ids'=>array(),'orphan_binding_ids'=>array()),
    );
}

function gic_registry_export_rest(WP_REST_Request $request) {
    return rest_ensure_response(gic_registry_export($request->get_param('workspace_id')));
}

function gic_registry_unit_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $code = sanitize_text_field($data['code'] ?? '');
    $name = sanitize_text_field($data['name'] ?? $code);
    $dimension = sanitize_key($data['dimension'] ?? 'custom');
    $workspace_id = sanitize_text_field($data['workspace_id'] ?? '');
    if (!$code || !$name) { return new WP_Error('gic_registry_invalid_unit','Unit code and name are required.',array('status'=>400)); }
    $unit_id = sanitize_text_field($data['unit_id'] ?? gic_registry_id('unit',array($workspace_id,strtolower($code))));
    $existing = $wpdb->get_row($wpdb->prepare("SELECT revision,created_at FROM " . gic_repository_table('units') . " WHERE unit_id=%s",$unit_id),ARRAY_A);
    $now=current_time('mysql',true);
    $wpdb->replace(gic_repository_table('units'),array('unit_id'=>$unit_id,'workspace_id'=>$workspace_id,'code'=>$code,'symbol'=>sanitize_text_field($data['symbol'] ?? ''),'name'=>$name,'dimension'=>$dimension,'canonical_unit_id'=>sanitize_text_field($data['canonical_unit_id'] ?? $unit_id),'scale_to_canonical'=>(float)($data['scale_to_canonical'] ?? 1),'offset_to_canonical'=>(float)($data['offset_to_canonical'] ?? 0),'precision_digits'=>(int)($data['precision_digits'] ?? 2),'lifecycle_status'=>'active','revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata']??array())));
    return rest_ensure_response(array('unit_id'=>$unit_id,'revision'=>$existing?((int)$existing['revision']+1):1));
}

function gic_registry_definition_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $workspace_id=sanitize_text_field($data['workspace_id']??''); $name=sanitize_text_field($data['name']??'');
    if(!$workspace_id||!$name){return new WP_Error('gic_registry_invalid_indicator','Workspace and indicator name are required.',array('status'=>400));}
    $unit=gic_registry_unit_by_code($data['unit']??'count',$workspace_id); if(!$unit){return new WP_Error('gic_registry_unknown_unit','The requested unit is not registered.',array('status'=>400));}
    $id=sanitize_text_field($data['indicator_definition_id']??gic_registry_id('indicator-definition',array($workspace_id,strtolower($name))));
    $doc=array('indicator_definition_id'=>$id,'workspace_id'=>$workspace_id,'name'=>$name,'description'=>sanitize_textarea_field($data['description']??''),'direction'=>sanitize_key($data['direction']??'higher_is_better'),'unit_id'=>$unit['unit_id'],'aggregation_method'=>sanitize_key($data['aggregation_method']??'latest'),'formula_expression'=>sanitize_textarea_field($data['formula_expression']??''),'formula_language'=>'gic-expression-1.0','disaggregation'=>(array)($data['disaggregation']??array()),'quality_profile'=>(array)($data['quality_profile']??array('status'=>'not_assessed')),'lifecycle_status'=>'draft','metadata'=>(array)($data['metadata']??array()));
    $version=gic_registry_store_version('indicator',$id,$doc,$data['version_label']??'1.0'); $now=current_time('mysql',true);
    $wpdb->replace(gic_repository_table('indicator_definitions'),array('indicator_definition_id'=>$id,'workspace_id'=>$workspace_id,'name'=>$name,'description'=>$doc['description'],'direction'=>$doc['direction'],'unit_id'=>$unit['unit_id'],'aggregation_method'=>$doc['aggregation_method'],'formula_expression'=>$doc['formula_expression'],'formula_language'=>'gic-expression-1.0','disaggregation_json'=>wp_json_encode($doc['disaggregation']),'quality_profile_json'=>wp_json_encode($doc['quality_profile']),'lifecycle_status'=>'draft','current_version'=>(int)($version['version_number']??1),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($doc['metadata'])));
    return rest_ensure_response(array('indicator_definition_id'=>$id,'version'=>$version));
}

function gic_registry_model_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $record_type=sanitize_key($request->get_param('record_type')); $workspace_id=sanitize_text_field($data['workspace_id']??''); $name=sanitize_text_field($data['name']??'');
    if(!$workspace_id||!$name){return new WP_Error('gic_registry_invalid_model','Workspace and name are required.',array('status'=>400));}
    $unit=gic_registry_unit_by_code($data['unit']??'count',$workspace_id); if(!$unit){return new WP_Error('gic_registry_unknown_unit','The requested unit is not registered.',array('status'=>400));}
    $now=current_time('mysql',true);
    if($record_type==='baseline'){
        $id=sanitize_text_field($data['baseline_model_id']??gic_registry_id('baseline-model',array($workspace_id,strtolower($name)))); $doc=array_merge($data,array('baseline_model_id'=>$id,'workspace_id'=>$workspace_id,'unit_id'=>$unit['unit_id'])); $version=gic_registry_store_version('baseline',$id,$doc,$data['version_label']??'1.0');
        $wpdb->replace(gic_repository_table('baseline_models'),array('baseline_model_id'=>$id,'workspace_id'=>$workspace_id,'name'=>$name,'method_type'=>sanitize_key($data['method_type']??'point_first'),'unit_id'=>$unit['unit_id'],'description'=>sanitize_textarea_field($data['description']??''),'benchmark_value'=>isset($data['benchmark_value'])?(float)$data['benchmark_value']:null,'rolling_periods'=>isset($data['rolling_periods'])?(int)$data['rolling_periods']:null,'formula_expression'=>sanitize_textarea_field($data['formula_expression']??''),'minimum_observations'=>(int)($data['minimum_observations']??1),'confidence'=>sanitize_key($data['confidence']??'medium'),'parameters_json'=>wp_json_encode($data['parameters']??array()),'lifecycle_status'=>'draft','current_version'=>(int)($version['version_number']??1),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata']??array()))); return rest_ensure_response(array('baseline_model_id'=>$id,'version'=>$version));
    }
    if($record_type==='target'){
        $id=sanitize_text_field($data['target_model_id']??gic_registry_id('target-model',array($workspace_id,strtolower($name)))); $doc=array_merge($data,array('target_model_id'=>$id,'workspace_id'=>$workspace_id,'unit_id'=>$unit['unit_id'])); $version=gic_registry_store_version('target',$id,$doc,$data['version_label']??'1.0');
        $wpdb->replace(gic_repository_table('target_models'),array('target_model_id'=>$id,'workspace_id'=>$workspace_id,'indicator_definition_id'=>sanitize_text_field($data['indicator_definition_id']??''),'name'=>$name,'target_type'=>sanitize_key($data['target_type']??'absolute'),'unit_id'=>$unit['unit_id'],'direction'=>sanitize_key($data['direction']??'higher_is_better'),'target_value'=>isset($data['target_value'])?(float)$data['target_value']:null,'lower_value'=>isset($data['lower_value'])?(float)$data['lower_value']:null,'upper_value'=>isset($data['upper_value'])?(float)$data['upper_value']:null,'relative_change_percent'=>isset($data['relative_change_percent'])?(float)$data['relative_change_percent']:null,'start_period'=>sanitize_text_field($data['start_period']??''),'end_period'=>sanitize_text_field($data['end_period']??''),'start_value'=>isset($data['start_value'])?(float)$data['start_value']:null,'end_value'=>isset($data['end_value'])?(float)$data['end_value']:null,'trajectory_type'=>sanitize_key($data['trajectory_type']??'linear'),'formula_expression'=>sanitize_textarea_field($data['formula_expression']??''),'milestones_json'=>wp_json_encode($data['milestones']??array()),'lifecycle_status'=>'draft','current_version'=>(int)($version['version_number']??1),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata']??array()))); return rest_ensure_response(array('target_model_id'=>$id,'version'=>$version));
    }
    return new WP_Error('gic_registry_invalid_model','Unsupported model type.',array('status'=>400));
}

function gic_registry_method_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $workspace_id=sanitize_text_field($data['workspace_id']??''); $name=sanitize_text_field($data['name']??'');
    if(!$workspace_id||!$name){return new WP_Error('gic_registry_invalid_method','Workspace and method name are required.',array('status'=>400));}
    $id=sanitize_text_field($data['method_definition_id']??gic_registry_id('method-definition',array($workspace_id,strtolower($name)))); $doc=array_merge($data,array('method_definition_id'=>$id,'workspace_id'=>$workspace_id)); $version=gic_registry_store_version('method',$id,$doc,$data['version_label']??'1.0'); $now=current_time('mysql',true);
    $wpdb->replace(gic_repository_table('method_definitions'),array('method_definition_id'=>$id,'workspace_id'=>$workspace_id,'name'=>$name,'method_kind'=>sanitize_key($data['method_kind']??'measurement'),'design_type'=>sanitize_key($data['design_type']??'monitoring'),'description'=>sanitize_textarea_field($data['description']??''),'formula_expression'=>sanitize_textarea_field($data['formula_expression']??''),'input_requirements_json'=>wp_json_encode($data['input_requirements']??array()),'quality_profile_json'=>wp_json_encode($data['quality_profile']??array()),'limitations_json'=>wp_json_encode($data['limitations']??array()),'lifecycle_status'=>'draft','current_version'=>(int)($version['version_number']??1),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata']??array())));
    return rest_ensure_response(array('method_definition_id'=>$id,'version'=>$version));
}

function gic_registry_register_routes() {
    register_rest_route('global-impact-catalyst/v1','/indicator-registry',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_registry_export_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/units',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_registry_unit_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/indicator-definitions',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_registry_definition_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/baseline-models',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_registry_model_rest','permission_callback'=>'gic_repository_can_edit','args'=>array('record_type'=>array('default'=>'baseline'))));
    register_rest_route('global-impact-catalyst/v1','/target-models',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_registry_model_rest','permission_callback'=>'gic_repository_can_edit','args'=>array('record_type'=>array('default'=>'target'))));
    register_rest_route('global-impact-catalyst/v1','/method-definitions',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_registry_method_rest','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init','gic_registry_register_routes');

function gic_indicator_registry_shortcode($atts = array()) {
    if (!is_user_logged_in() || !current_user_can('edit_posts')) {
        return '<section class="gic-registry"><p>Sign in with editing access to use the Indicator Registry.</p></section>';
    }
    static $instance = 0; $instance++;
    $prefix = 'gic-registry-' . $instance . '-' . wp_rand(1000,999999);
    $id = static function($name) use ($prefix) { return esc_attr($prefix . '-' . $name); };
    wp_enqueue_style('global-impact-catalyst-registry'); wp_enqueue_script('global-impact-catalyst-registry');
    wp_localize_script('global-impact-catalyst-registry','GICRegistryConfig',array('restRoot'=>esc_url_raw(rest_url('global-impact-catalyst/v1/')),'nonce'=>wp_create_nonce('wp_rest')));
    ob_start(); ?>
    <section class="gic-registry" data-gic-indicator-registry>
      <header class="gic-registry__header"><p class="gic-registry__eyebrow">Indicator governance · v1.4.0</p><h2>Indicator Registry</h2><p>Define reusable indicators, units, baselines, targets, trajectories, formulas, and measurement methods without changing the canonical v1.1.0 calculation contract.</p></header>
      <div class="gic-registry__toolbar"><label for="<?php echo $id('workspace'); ?>">Workspace ID</label><input id="<?php echo $id('workspace'); ?>" data-gic-registry-workspace type="text" placeholder="gic-workspace-…"><button type="button" data-gic-registry-load>Load registry</button><button type="button" data-gic-registry-download>Download JSON</button></div>
      <div class="gic-registry__status" data-gic-registry-status role="status">Enter a workspace ID to load its governed registry.</div>
      <div class="gic-registry__summary" data-gic-registry-summary></div>
      <div class="gic-registry__grid">
        <form data-gic-unit-form><h3>Register unit</h3><input name="code" required placeholder="Unit code"><input name="name" required placeholder="Unit name"><input name="dimension" required placeholder="Dimension"><button type="submit">Save unit</button></form>
        <form data-gic-indicator-form><h3>Register indicator</h3><input name="name" required placeholder="Indicator name"><input name="unit" required placeholder="Unit code"><select name="direction"><option value="higher_is_better">Higher is better</option><option value="lower_is_better">Lower is better</option><option value="neutral">Neutral</option></select><textarea name="description" placeholder="Definition"></textarea><button type="submit">Save indicator</button></form>
        <form data-gic-baseline-form><h3>Register baseline model</h3><input name="name" required placeholder="Baseline model name"><input name="unit" required placeholder="Unit code"><select name="method_type"><option value="point_first">First observation</option><option value="period_average">Period average</option><option value="rolling_average">Rolling average</option><option value="benchmark">Benchmark</option><option value="modelled">Formula</option></select><input name="benchmark_value" type="number" step="any" placeholder="Benchmark value"><button type="submit">Save baseline</button></form>
        <form data-gic-target-form><h3>Register target model</h3><input name="name" required placeholder="Target model name"><input name="unit" required placeholder="Unit code"><select name="target_type"><option value="absolute">Absolute</option><option value="relative_change">Relative change</option><option value="range">Range</option><option value="trajectory">Trajectory</option><option value="formula">Formula</option></select><input name="target_value" type="number" step="any" placeholder="Target value"><button type="submit">Save target</button></form>
        <form data-gic-method-form><h3>Register method</h3><input name="name" required placeholder="Method name"><select name="design_type"><option value="monitoring">Monitoring</option><option value="before_after">Before and after</option><option value="comparison_group">Comparison group</option><option value="quasi_experimental">Quasi-experimental</option><option value="randomized">Randomized</option><option value="qualitative">Qualitative</option><option value="mixed_methods">Mixed methods</option></select><textarea name="description" placeholder="Method description"></textarea><button type="submit">Save method</button></form>
      </div>
      <div class="gic-registry__records" data-gic-registry-records></div>
      <p class="gic-registry__boundary">Registry validation checks structure, unit compatibility, and method transparency. It does not establish truth, causal proof, assurance, certification, or audit status.</p>
    </section>
    <?php return ob_get_clean();
}
add_shortcode('global_impact_catalyst_indicator_registry','gic_indicator_registry_shortcode');

/** Multi-period measurement and outcome portfolio layer introduced in v1.5.0. */
function gic_measurement_id($kind, $parts = array()) {
    return 'gic-' . sanitize_key($kind) . '-' . substr(hash('sha256', wp_json_encode(array_values((array) $parts))), 0, 20);
}

function gic_measurement_period($data) {
    $period = isset($data['period']) && is_array($data['period']) ? $data['period'] : array();
    $start = sanitize_text_field($data['period_start'] ?? ($period['start'] ?? ''));
    $end = sanitize_text_field($data['period_end'] ?? ($period['end'] ?? ''));
    $label = sanitize_text_field($data['period_label'] ?? ($period['label'] ?? ''));
    if (!$label) { $label = trim($start . '/' . $end, '/'); }
    if (!$label) { $label = 'Unspecified period'; }
    return array($start, $end, $label);
}

function gic_measurement_dimensions($value) {
    $value = is_array($value) ? $value : array();
    $forbidden = array('name','full_name','first_name','last_name','email','email_address','phone','phone_number','address','street_address','ssn','date_of_birth','dob','passport','person_id','individual_id','patient_id');
    $clean = array();
    foreach ($value as $key => $item) {
        $normalized = sanitize_key($key);
        if (in_array($normalized, $forbidden, true)) {
            return new WP_Error('gic_measurement_privacy_boundary', 'Direct identifier dimensions are not allowed in aggregate measurement records.', array('status'=>400));
        }
        if (is_array($item)) {
            foreach ($item as $subitem) {
                if (is_array($subitem) || is_object($subitem)) {
                    return new WP_Error('gic_measurement_privacy_boundary', 'Nested person-level dimension values are not allowed.', array('status'=>400));
                }
            }
            $clean[$normalized] = array_map('sanitize_text_field', $item);
        } elseif (is_scalar($item) || is_null($item)) {
            $clean[$normalized] = is_string($item) ? sanitize_text_field($item) : $item;
        } else {
            return new WP_Error('gic_measurement_invalid_dimension', 'Unsupported dimension value.', array('status'=>400));
        }
    }
    return $clean;
}

function gic_measurement_decode_rows($table, $workspace_id, $json_fields = array('metadata_json')) {
    global $wpdb;
    $rows = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$table} WHERE workspace_id=%s ORDER BY 1", sanitize_text_field($workspace_id)), ARRAY_A);
    foreach ($rows as &$row) {
        foreach ($json_fields as $field) {
            $name = preg_replace('/_json$/', '', $field);
            $row[$name] = json_decode($row[$field] ?? '', true) ?: array();
            unset($row[$field]);
        }
    }
    return $rows;
}

function gic_measurement_repository_export($workspace_id) {
    global $wpdb;
    $workspace_id = sanitize_text_field($workspace_id);
    $results = gic_measurement_decode_rows(gic_repository_table('impact_results'), $workspace_id);
    $relationships = gic_measurement_decode_rows(gic_repository_table('result_relationships'), $workspace_id);
    $observations = gic_measurement_decode_rows(gic_repository_table('observation_series'), $workspace_id, array('dimensions_json','denominator_json','metadata_json'));
    $definitions = gic_measurement_decode_rows(gic_repository_table('beneficiary_definitions'), $workspace_id);
    $beneficiary_observations = gic_measurement_decode_rows(gic_repository_table('beneficiary_observations'), $workspace_id, array('dimensions_json','metadata_json'));
    $financial = gic_measurement_decode_rows(gic_repository_table('financial_records'), $workspace_id);
    $factors = gic_measurement_decode_rows(gic_repository_table('external_factors'), $workspace_id);
    $notes = gic_measurement_decode_rows(gic_repository_table('contribution_notes'), $workspace_id, array('evidence_refs_json','external_factor_refs_json','metadata_json'));
    $portfolios = gic_measurement_decode_rows(gic_repository_table('outcome_portfolios'), $workspace_id);
    $members_table = gic_repository_table('outcome_portfolio_members');
    foreach ($portfolios as &$portfolio) {
        $members = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$members_table} WHERE outcome_portfolio_id=%s ORDER BY position,membership_id", $portfolio['outcome_portfolio_id']), ARRAY_A);
        foreach ($members as &$member) { $member['metadata'] = json_decode($member['metadata_json'] ?? '', true) ?: array(); unset($member['metadata_json']); }
        $portfolio['members'] = $members;
    }
    $runs = gic_measurement_decode_rows(gic_repository_table('portfolio_aggregation_runs'), $workspace_id, array('result_json'));
    return array(
        'repository_type'=>'global_impact_measurement_repository','repository_version'=>'1.5.0','workspace_id'=>$workspace_id,
        'generated_at'=>gmdate('c'),'impact_results'=>$results,'impact_result_relationships'=>$relationships,
        'observations'=>$observations,'beneficiary_definitions'=>$definitions,'beneficiary_observations'=>$beneficiary_observations,
        'financial_records'=>$financial,'external_factors'=>$factors,'contribution_notes'=>$notes,
        'outcome_portfolios'=>$portfolios,'portfolio_aggregation_runs'=>$runs,
        'integrity'=>array('valid'=>true,'impact_result_count'=>count($results),'observation_count'=>count($observations),
            'beneficiary_definition_count'=>count($definitions),'beneficiary_observation_count'=>count($beneficiary_observations),
            'financial_record_count'=>count($financial),'external_factor_count'=>count($factors),
            'contribution_note_count'=>count($notes),'outcome_portfolio_count'=>count($portfolios),
            'aggregation_run_count'=>count($runs),'orphan_relationship_ids'=>array(),'forbidden_dimension_keys'=>array()),
        'privacy_boundary'=>'The core repository stores aggregate beneficiary counts and dimensions, not individual beneficiary records.',
    );
}

function gic_measurement_export_rest(WP_REST_Request $request) {
    return rest_ensure_response(gic_measurement_repository_export($request->get_param('workspace_id')));
}

function gic_measurement_observation_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $workspace_id = sanitize_text_field($data['workspace_id'] ?? '');
    $initiative_id = sanitize_text_field($data['initiative_id'] ?? '');
    $indicator_id = sanitize_text_field($data['indicator_id'] ?? '');
    $state = sanitize_key($data['data_state'] ?? 'complete');
    $allowed_states = array('complete','missing','late','revised','partial');
    if (!$workspace_id || !$initiative_id || !$indicator_id || !in_array($state, $allowed_states, true)) {
        return new WP_Error('gic_measurement_invalid_observation', 'Workspace, initiative, indicator, and a supported data state are required.', array('status'=>400));
    }
    $dimensions = gic_measurement_dimensions($data['dimensions'] ?? array());
    if (is_wp_error($dimensions)) { return $dimensions; }
    $value = array_key_exists('value', $data) && $data['value'] !== '' ? (float) $data['value'] : null;
    if ($state === 'missing' && $value !== null) { return new WP_Error('gic_measurement_missing_value','Missing observations must not include a value.',array('status'=>400)); }
    if ($state !== 'missing' && $value === null) { return new WP_Error('gic_measurement_required_value','Non-missing observations require a value.',array('status'=>400)); }
    list($start,$end,$label) = gic_measurement_period($data);
    $unit = gic_registry_unit_by_code($data['unit_id'] ?? ($data['unit'] ?? 'count'), $workspace_id);
    if (!$unit) { return new WP_Error('gic_measurement_unknown_unit','The requested unit is not registered.',array('status'=>400)); }
    $id = sanitize_text_field($data['observation_record_id'] ?? gic_measurement_id('observation-record', array($initiative_id,$indicator_id,$label,$dimensions,$data['revision_of_observation_id'] ?? 'base',$value)));
    $existing = $wpdb->get_row($wpdb->prepare("SELECT revision,created_at FROM " . gic_repository_table('observation_series') . " WHERE observation_record_id=%s", $id), ARRAY_A);
    $now = current_time('mysql', true);
    $wpdb->replace(gic_repository_table('observation_series'), array(
        'observation_record_id'=>$id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,'indicator_id'=>$indicator_id,
        'indicator_definition_id'=>sanitize_text_field($data['indicator_definition_id'] ?? ''),'impact_result_id'=>sanitize_text_field($data['impact_result_id'] ?? ''),
        'period_start'=>$start ?: null,'period_end'=>$end ?: null,'period_label'=>$label,'value'=>$value,'unit_id'=>$unit['unit_id'],'data_state'=>$state,
        'revision_of_observation_id'=>sanitize_text_field($data['revision_of_observation_id'] ?? ''),'received_at'=>$now,
        'revised_at'=>$state==='revised'?$now:null,'source_id'=>sanitize_text_field($data['source_id'] ?? ''),
        'method_definition_id'=>sanitize_text_field($data['method_definition_id'] ?? ''),'dimensions_json'=>wp_json_encode($dimensions),
        'denominator_json'=>wp_json_encode((array)($data['denominator'] ?? array())),'notes'=>sanitize_textarea_field($data['notes'] ?? ''),
        'revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,
        'metadata_json'=>wp_json_encode((array)($data['metadata'] ?? array())),
    ));
    return rest_ensure_response(array('observation_record_id'=>$id,'revision'=>$existing?((int)$existing['revision']+1):1,'data_state'=>$state,'period_label'=>$label));
}

function gic_measurement_beneficiary_definition_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $workspace_id=sanitize_text_field($data['workspace_id']??''); $initiative_id=sanitize_text_field($data['initiative_id']??''); $name=sanitize_text_field($data['name']??'');
    if(!$workspace_id||!$initiative_id||!$name){return new WP_Error('gic_measurement_invalid_beneficiary','Workspace, initiative, and beneficiary definition name are required.',array('status'=>400));}
    $id=sanitize_text_field($data['beneficiary_definition_id']??gic_measurement_id('beneficiary-definition',array($initiative_id,strtolower($name),$data['reach_type']??'direct'))); $now=current_time('mysql',true);
    $existing=$wpdb->get_row($wpdb->prepare("SELECT revision,created_at FROM ".gic_repository_table('beneficiary_definitions')." WHERE beneficiary_definition_id=%s",$id),ARRAY_A);
    $wpdb->replace(gic_repository_table('beneficiary_definitions'),array('beneficiary_definition_id'=>$id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,'name'=>$name,'description'=>sanitize_textarea_field($data['description']??''),'reach_type'=>sanitize_key($data['reach_type']??'direct'),'counting_method'=>sanitize_key($data['counting_method']??'unique'),'privacy_level'=>sanitize_key($data['privacy_level']??'aggregate_only'),'overlap_policy'=>sanitize_key($data['overlap_policy']??'unknown'),'overlap_notes'=>sanitize_textarea_field($data['overlap_notes']??''),'lifecycle_status'=>'draft','revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode((array)($data['metadata']??array()))));
    return rest_ensure_response(array('beneficiary_definition_id'=>$id,'revision'=>$existing?((int)$existing['revision']+1):1));
}

function gic_measurement_beneficiary_observation_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $definition_id=sanitize_text_field($data['beneficiary_definition_id']??'');
    $definition=$wpdb->get_row($wpdb->prepare("SELECT * FROM ".gic_repository_table('beneficiary_definitions')." WHERE beneficiary_definition_id=%s",$definition_id),ARRAY_A);
    if(!$definition){return new WP_Error('gic_measurement_unknown_beneficiary','Beneficiary definition not found.',array('status'=>404));}
    $dimensions=gic_measurement_dimensions($data['dimensions']??array()); if(is_wp_error($dimensions)){return $dimensions;}
    $state=sanitize_key($data['data_state']??'complete'); $count=array_key_exists('observed_count',$data)&&$data['observed_count']!==''?(float)$data['observed_count']:null;
    if($state==='missing'&&$count!==null){return new WP_Error('gic_measurement_missing_count','Missing beneficiary observations must not include a count.',array('status'=>400));}
    if($state!=='missing'&&$count===null){return new WP_Error('gic_measurement_required_count','Non-missing beneficiary observations require a count.',array('status'=>400));}
    list($start,$end,$label)=gic_measurement_period($data); $id=sanitize_text_field($data['beneficiary_observation_id']??gic_measurement_id('beneficiary-observation',array($definition_id,$label,$dimensions,$count))); $now=current_time('mysql',true);
    $existing=$wpdb->get_row($wpdb->prepare("SELECT revision,created_at FROM ".gic_repository_table('beneficiary_observations')." WHERE beneficiary_observation_id=%s",$id),ARRAY_A);
    $wpdb->replace(gic_repository_table('beneficiary_observations'),array('beneficiary_observation_id'=>$id,'beneficiary_definition_id'=>$definition_id,'workspace_id'=>$definition['workspace_id'],'initiative_id'=>$definition['initiative_id'],'period_start'=>$start?:null,'period_end'=>$end?:null,'period_label'=>$label,'observed_count'=>$count,'data_state'=>$state,'revision_of_observation_id'=>sanitize_text_field($data['revision_of_observation_id']??''),'dimensions_json'=>wp_json_encode($dimensions),'overlap_estimate'=>isset($data['overlap_estimate'])?(float)$data['overlap_estimate']:null,'denominator_notes'=>sanitize_textarea_field($data['denominator_notes']??''),'source_id'=>sanitize_text_field($data['source_id']??''),'received_at'=>$now,'revised_at'=>$state==='revised'?$now:null,'revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode((array)($data['metadata']??array()))));
    return rest_ensure_response(array('beneficiary_observation_id'=>$id,'revision'=>$existing?((int)$existing['revision']+1):1));
}

function gic_measurement_financial_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $workspace_id=sanitize_text_field($data['workspace_id']??''); $initiative_id=sanitize_text_field($data['initiative_id']??''); $type=sanitize_key($data['record_type']??'expenditure');
    if(!$workspace_id||!$initiative_id||!in_array($type,array('budget','expenditure','commitment','funding'),true)){return new WP_Error('gic_measurement_invalid_financial','Workspace, initiative, and a supported financial record type are required.',array('status'=>400));}
    $state=sanitize_key($data['data_state']??'complete'); $amount=array_key_exists('amount',$data)&&$data['amount']!==''?(float)$data['amount']:null; $currency=strtoupper(sanitize_text_field($data['currency']??'USD')); $reporting=strtoupper(sanitize_text_field($data['reporting_currency']??$currency)); $rate=isset($data['exchange_rate'])?(float)$data['exchange_rate']:null;
    if($amount!==null&&$currency!==$reporting&&(!$rate||$rate<=0)){return new WP_Error('gic_measurement_exchange_rate','Cross-currency records require a positive explicit exchange rate.',array('status'=>400));}
    $reporting_amount=$amount===null?null:$amount*($currency===$reporting?($rate?:1):$rate); list($start,$end,$label)=gic_measurement_period($data);
    $id=sanitize_text_field($data['financial_record_id']??gic_measurement_id('financial-record',array($initiative_id,$type,$label,$currency,$data['cost_category']??'uncategorized',$amount))); $now=current_time('mysql',true); $existing=$wpdb->get_row($wpdb->prepare("SELECT revision,created_at FROM ".gic_repository_table('financial_records')." WHERE financial_record_id=%s",$id),ARRAY_A);
    $wpdb->replace(gic_repository_table('financial_records'),array('financial_record_id'=>$id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,'record_type'=>$type,'funding_source'=>sanitize_text_field($data['funding_source']??''),'cost_category'=>sanitize_key($data['cost_category']??'uncategorized'),'period_start'=>$start?:null,'period_end'=>$end?:null,'period_label'=>$label,'amount'=>$amount,'currency'=>$currency,'reporting_currency'=>$reporting,'exchange_rate'=>$currency===$reporting?($rate?:1):$rate,'reporting_amount'=>$reporting_amount,'data_state'=>$state,'source_id'=>sanitize_text_field($data['source_id']??''),'notes'=>sanitize_textarea_field($data['notes']??''),'revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode((array)($data['metadata']??array()))));
    return rest_ensure_response(array('financial_record_id'=>$id,'reporting_amount'=>$reporting_amount,'reporting_currency'=>$reporting));
}

function gic_measurement_portfolio_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $workspace_id=sanitize_text_field($data['workspace_id']??''); $name=sanitize_text_field($data['name']??'');
    if(!$workspace_id||!$name){return new WP_Error('gic_measurement_invalid_portfolio','Workspace and portfolio name are required.',array('status'=>400));}
    $id=sanitize_text_field($data['outcome_portfolio_id']??gic_measurement_id('outcome-portfolio',array($workspace_id,strtolower($name)))); $now=current_time('mysql',true); $existing=$wpdb->get_row($wpdb->prepare("SELECT revision,created_at FROM ".gic_repository_table('outcome_portfolios')." WHERE outcome_portfolio_id=%s",$id),ARRAY_A);
    $unit=gic_registry_unit_by_code($data['target_unit_id']??($data['target_unit']??''),$workspace_id);
    $wpdb->replace(gic_repository_table('outcome_portfolios'),array('outcome_portfolio_id'=>$id,'workspace_id'=>$workspace_id,'name'=>$name,'description'=>sanitize_textarea_field($data['description']??''),'aggregation_method'=>sanitize_key($data['aggregation_method']??'sum'),'target_unit_id'=>$unit['unit_id']??'','period_policy'=>sanitize_key($data['period_policy']??'exact'),'overlap_policy'=>sanitize_key($data['overlap_policy']??'exclude_unknown_or_overlapping'),'missing_data_policy'=>sanitize_key($data['missing_data_policy']??'exclude_and_disclose'),'archived_at'=>null,'revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode((array)($data['metadata']??array()))));
    return rest_ensure_response(array('outcome_portfolio_id'=>$id,'revision'=>$existing?((int)$existing['revision']+1):1));
}

function gic_measurement_portfolio_member_rest(WP_REST_Request $request) {
    global $wpdb;
    $data=$request->get_json_params(); $portfolio_id=sanitize_text_field($data['outcome_portfolio_id']??''); $initiative_id=sanitize_text_field($data['initiative_id']??''); $indicator_id=sanitize_text_field($data['indicator_id']??'');
    if(!$portfolio_id||!$initiative_id||!$indicator_id){return new WP_Error('gic_measurement_invalid_member','Portfolio, initiative, and indicator are required.',array('status'=>400));}
    $membership_id=sanitize_text_field($data['membership_id']??gic_measurement_id('outcome-membership',array($portfolio_id,$initiative_id,$indicator_id,$data['impact_result_id']??'')));
    $wpdb->replace(gic_repository_table('outcome_portfolio_members'),array('outcome_portfolio_id'=>$portfolio_id,'membership_id'=>$membership_id,'initiative_id'=>$initiative_id,'indicator_id'=>$indicator_id,'indicator_definition_id'=>sanitize_text_field($data['indicator_definition_id']??''),'impact_result_id'=>sanitize_text_field($data['impact_result_id']??''),'population_scope'=>sanitize_text_field($data['population_scope']??''),'overlap_group'=>sanitize_text_field($data['overlap_group']??''),'denominator_definition'=>sanitize_textarea_field($data['denominator_definition']??''),'weight'=>isset($data['weight'])?(float)$data['weight']:1,'position'=>isset($data['position'])?(int)$data['position']:0,'added_at'=>current_time('mysql',true),'metadata_json'=>wp_json_encode((array)($data['metadata']??array()))));
    return rest_ensure_response(array('membership_id'=>$membership_id,'outcome_portfolio_id'=>$portfolio_id));
}

function gic_measurement_portfolio_aggregate_rest(WP_REST_Request $request) {
    global $wpdb;
    $portfolio_id=sanitize_text_field($request['portfolio_id']); $data=$request->get_json_params(); $period_label=sanitize_text_field($data['period_label']??'');
    $portfolio=$wpdb->get_row($wpdb->prepare("SELECT * FROM ".gic_repository_table('outcome_portfolios')." WHERE outcome_portfolio_id=%s",$portfolio_id),ARRAY_A);
    if(!$portfolio){return new WP_Error('gic_measurement_unknown_portfolio','Outcome portfolio not found.',array('status'=>404));}
    $members=$wpdb->get_results($wpdb->prepare("SELECT * FROM ".gic_repository_table('outcome_portfolio_members')." WHERE outcome_portfolio_id=%s ORDER BY position,membership_id",$portfolio_id),ARRAY_A);
    $included=array(); $excluded=array(); $values=array(); $groups=array();
    foreach($members as $member){
        $query="SELECT * FROM ".gic_repository_table('observation_series')." WHERE initiative_id=%s AND indicator_id=%s"; $params=array($member['initiative_id'],$member['indicator_id']);
        if($period_label){$query.=" AND period_label=%s";$params[]=$period_label;} $query.=" ORDER BY received_at DESC LIMIT 1";
        $observation=$wpdb->get_row($wpdb->prepare($query,$params),ARRAY_A);
        if(!$observation||$observation['value']===null||in_array($observation['data_state'],array('missing','late'),true)){ $excluded[]=array('membership_id'=>$member['membership_id'],'reason'=>'period_or_observation_missing'); continue; }
        if($observation['data_state']==='partial'&&$portfolio['missing_data_policy']!=='include_partial'){ $excluded[]=array('membership_id'=>$member['membership_id'],'reason'=>'partial_period_excluded'); continue; }
        $group=$member['overlap_group']; if($portfolio['aggregation_method']==='sum'&&$member['denominator_definition']){
            if(!$group&&$portfolio['overlap_policy']==='exclude_unknown_or_overlapping'){ $excluded[]=array('membership_id'=>$member['membership_id'],'reason'=>'population_overlap_unknown'); continue; }
            if($group&&isset($groups[$group])&&$portfolio['overlap_policy']==='exclude_unknown_or_overlapping'){ $excluded[]=array('membership_id'=>$member['membership_id'],'reason'=>'overlapping_population','overlap_group'=>$group); continue; }
            if($group){$groups[$group]=true;}
        }
        if($portfolio['target_unit_id']&&$observation['unit_id']!==$portfolio['target_unit_id']){ $excluded[]=array('membership_id'=>$member['membership_id'],'reason'=>'incompatible_unit','unit_id'=>$observation['unit_id']); continue; }
        $value=(float)$observation['value']; $values[]=array('value'=>$value,'weight'=>(float)$member['weight']); $included[]=array('membership_id'=>$member['membership_id'],'observation_record_id'=>$observation['observation_record_id'],'converted_value'=>$value,'target_unit_id'=>$portfolio['target_unit_id']?:$observation['unit_id'],'period_label'=>$observation['period_label']);
    }
    $result_value=null; if($values){$plain=array_column($values,'value'); switch($portfolio['aggregation_method']){case'mean':$result_value=array_sum($plain)/count($plain);break;case'weighted_mean':$weight=array_sum(array_column($values,'weight'));$result_value=$weight?array_sum(array_map(function($v){return $v['value']*$v['weight'];},$values))/$weight:null;break;case'minimum':$result_value=min($plain);break;case'maximum':$result_value=max($plain);break;default:$result_value=array_sum($plain);}}
    $result=array('aggregation_type'=>'global_impact_outcome_portfolio_aggregation','aggregation_version'=>'1.5.0','outcome_portfolio_id'=>$portfolio_id,'workspace_id'=>$portfolio['workspace_id'],'generated_at'=>gmdate('c'),'period'=>array('start'=>null,'end'=>null,'label'=>$period_label?:'latest compatible period'),'aggregation_method'=>$portfolio['aggregation_method'],'target_unit_id'=>$portfolio['target_unit_id']?:null,'value'=>$result_value,'included'=>$included,'excluded'=>$excluded,'warnings'=>array(),'rules'=>array('period_policy'=>$portfolio['period_policy'],'overlap_policy'=>$portfolio['overlap_policy'],'missing_data_policy'=>$portfolio['missing_data_policy']),'integrity'=>array('valid'=>$result_value!==null,'included_count'=>count($included),'excluded_count'=>count($excluded)),'boundary'=>'Portfolio aggregation combines compatible recorded observations; it does not prove attribution or eliminate double-counting risk beyond disclosed rules.');
    $run_id=gic_measurement_id('portfolio-run',array($portfolio_id,microtime(true),$period_label,$result_value)); $wpdb->insert(gic_repository_table('portfolio_aggregation_runs'),array('aggregation_run_id'=>$run_id,'outcome_portfolio_id'=>$portfolio_id,'workspace_id'=>$portfolio['workspace_id'],'period_start'=>null,'period_end'=>null,'period_label'=>$period_label,'aggregation_method'=>$portfolio['aggregation_method'],'target_unit_id'=>$portfolio['target_unit_id'],'result_value'=>$result_value,'result_json'=>wp_json_encode($result),'created_at'=>current_time('mysql',true),'created_by'=>get_current_user_id())); $result['aggregation_run_id']=$run_id;
    return rest_ensure_response($result);
}

function gic_measurement_register_routes() {
    register_rest_route('global-impact-catalyst/v1','/measurement-repository',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_measurement_export_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/observations',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_measurement_observation_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/beneficiary-definitions',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_measurement_beneficiary_definition_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/beneficiary-observations',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_measurement_beneficiary_observation_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/financial-records',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_measurement_financial_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/outcome-portfolios',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_measurement_portfolio_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/outcome-portfolio-members',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_measurement_portfolio_member_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/outcome-portfolios/(?P<portfolio_id>[A-Za-z0-9_-]+)/aggregate',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_measurement_portfolio_aggregate_rest','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init','gic_measurement_register_routes');

function gic_measurement_portfolio_shortcode($atts = array()) {
    if (!is_user_logged_in() || !current_user_can('edit_posts')) {
        return '<section class="gic-measurement"><p>Sign in with editing access to use program measurement and outcome portfolios.</p></section>';
    }
    static $instance=0; $instance++; $prefix='gic-measurement-'.$instance.'-'.wp_rand(1000,999999);
    $id=static function($name)use($prefix){return esc_attr($prefix.'-'.$name);};
    wp_enqueue_style('global-impact-catalyst-measurement'); wp_enqueue_script('global-impact-catalyst-measurement');
    wp_localize_script('global-impact-catalyst-measurement','GICMeasurementConfig',array('restRoot'=>esc_url_raw(rest_url('global-impact-catalyst/v1/')),'nonce'=>wp_create_nonce('wp_rest')));
    ob_start(); ?>
    <section class="gic-measurement" data-gic-measurement-portfolio>
      <header class="gic-measurement__header"><p class="gic-measurement__eyebrow">Program measurement · v1.5.0</p><h2>Observations, Beneficiaries, Budgets, and Outcome Portfolios</h2><p>Record aggregate observations across periods, disclose beneficiary counting and overlap assumptions, track resources, and aggregate only compatible portfolio members.</p></header>
      <div class="gic-measurement__toolbar"><label for="<?php echo $id('workspace'); ?>">Workspace ID</label><input id="<?php echo $id('workspace'); ?>" data-gic-measurement-workspace placeholder="gic-workspace-…"><label for="<?php echo $id('initiative'); ?>">Initiative ID</label><input id="<?php echo $id('initiative'); ?>" data-gic-measurement-initiative placeholder="gic-initiative-…"><button type="button" data-gic-measurement-load>Load repository</button><button type="button" data-gic-measurement-download>Download JSON</button></div>
      <div class="gic-measurement__status" data-gic-measurement-status role="status">Enter a workspace ID to load its measurement repository.</div>
      <div class="gic-measurement__summary" data-gic-measurement-summary></div>
      <div class="gic-measurement__grid">
        <form data-gic-observation-form><h3>Record observation</h3><input name="indicator_id" required placeholder="Indicator ID"><input name="period_label" required placeholder="Reporting period"><input name="value" type="number" step="any" placeholder="Value"><input name="unit" required placeholder="Unit code"><select name="data_state"><option value="complete">Complete</option><option value="partial">Partial period</option><option value="late">Late</option><option value="missing">Missing</option><option value="revised">Revised</option></select><input name="geography" placeholder="Geography"><input name="population_group" placeholder="Population group"><button type="submit">Save observation</button></form>
        <form data-gic-beneficiary-form><h3>Define beneficiaries</h3><input name="name" required placeholder="Beneficiary definition"><select name="reach_type"><option value="direct">Direct reach</option><option value="indirect">Indirect reach</option><option value="combined">Combined reach</option></select><select name="counting_method"><option value="unique">Unique count</option><option value="estimated_unique">Estimated unique</option><option value="encounters">Encounters</option><option value="households">Households</option><option value="organizations">Organizations</option></select><select name="overlap_policy"><option value="unknown">Overlap unknown</option><option value="no_overlap">No overlap</option><option value="estimated_overlap">Estimated overlap</option><option value="known_overlap">Known overlap</option></select><button type="submit">Save definition</button></form>
        <form data-gic-beneficiary-observation-form><h3>Record beneficiary count</h3><input name="beneficiary_definition_id" required placeholder="Beneficiary definition ID"><input name="period_label" required placeholder="Reporting period"><input name="observed_count" type="number" min="0" step="any" placeholder="Aggregate count"><input name="overlap_estimate" type="number" min="0" step="any" placeholder="Estimated overlap"><input name="age_band" placeholder="Age band"><button type="submit">Save aggregate count</button></form>
        <form data-gic-financial-form><h3>Record resources</h3><select name="record_type"><option value="expenditure">Expenditure</option><option value="budget">Budget</option><option value="commitment">Commitment</option><option value="funding">Funding</option></select><input name="period_label" required placeholder="Reporting period"><input name="amount" type="number" min="0" step="any" required placeholder="Amount"><input name="currency" value="USD" required placeholder="Currency"><input name="reporting_currency" value="USD" required placeholder="Reporting currency"><input name="exchange_rate" type="number" min="0" step="any" placeholder="Exchange rate"><input name="cost_category" placeholder="Cost category"><button type="submit">Save financial record</button></form>
        <form data-gic-outcome-portfolio-form><h3>Create outcome portfolio</h3><input name="name" required placeholder="Portfolio name"><input name="target_unit" placeholder="Target unit code"><select name="aggregation_method"><option value="sum">Sum</option><option value="mean">Mean</option><option value="weighted_mean">Weighted mean</option><option value="minimum">Minimum</option><option value="maximum">Maximum</option></select><select name="overlap_policy"><option value="exclude_unknown_or_overlapping">Exclude overlap or unknown scope</option><option value="allow_with_disclosure">Allow with disclosure</option><option value="fail_on_overlap">Stop on overlap</option></select><button type="submit">Create portfolio</button></form>
        <form data-gic-outcome-member-form><h3>Add portfolio member</h3><input name="outcome_portfolio_id" required placeholder="Outcome portfolio ID"><input name="member_initiative_id" required placeholder="Initiative ID"><input name="indicator_id" required placeholder="Indicator ID"><input name="population_scope" placeholder="Population scope"><input name="overlap_group" placeholder="Overlap group"><input name="denominator_definition" placeholder="Denominator definition"><button type="submit">Add member</button></form>
        <form data-gic-outcome-aggregate-form><h3>Aggregate portfolio</h3><input name="outcome_portfolio_id" required placeholder="Outcome portfolio ID"><input name="period_label" required placeholder="Reporting period"><button type="submit">Run guarded aggregation</button></form>
      </div>
      <div class="gic-measurement__records" data-gic-measurement-records></div>
      <p class="gic-measurement__boundary">Core workflows store aggregate beneficiary records only. Portfolio totals expose unit, period, missing-data, and population-overlap exclusions and do not establish causal attribution.</p>
    </section>
    <?php return ob_get_clean();
}
add_shortcode('global_impact_catalyst_measurement_portfolio','gic_measurement_portfolio_shortcode');

/** Review, quality, revision, correction, and publication workflow introduced in v1.6.0. */
function gic_review_id($kind, $parts) {
    return 'gic-' . sanitize_key($kind) . '-' . substr(hash('sha256', implode('|', array_map('strval', $parts))), 0, 20);
}

function gic_review_ensure_roles($workspace_id) {
    global $wpdb;
    $table = gic_repository_table('workflow_roles');
    $now = current_time('mysql', true);
    $roles = array(
        'program_owner' => array('Program Owner', array('edit','submit_review','respond_review','open_correction')),
        'evidence_reviewer' => array('Evidence Reviewer', array('review_evidence','comment','assess_quality','request_changes')),
        'methods_reviewer' => array('Methods Reviewer', array('review_methods','comment','assess_quality','request_changes')),
        'approver' => array('Approver', array('comment','assess_quality','approve','reject')),
        'publisher' => array('Publisher', array('publish','withdraw','supersede')),
    );
    foreach ($roles as $key => $definition) {
        $role_id = gic_review_id('role', array($workspace_id, $key));
        if (!$wpdb->get_var($wpdb->prepare("SELECT role_id FROM {$table} WHERE role_id=%s", $role_id))) {
            $wpdb->insert($table, array(
                'role_id'=>$role_id,'workspace_id'=>$workspace_id,'name'=>$definition[0],
                'description'=>'System role for ' . strtolower($definition[0]) . ' workflow responsibilities.',
                'permissions_json'=>wp_json_encode($definition[1]),'is_system'=>1,'archived_at'=>null,
                'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode(array('role_key'=>$key)),
            ));
        }
    }
}

function gic_review_decode_rows($table, $workspace_id, $json_fields = array()) {
    global $wpdb;
    $rows = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$table} WHERE workspace_id=%s ORDER BY 1", $workspace_id), ARRAY_A);
    foreach ($rows as &$row) {
        foreach ($json_fields as $field) {
            if (array_key_exists($field . '_json', $row)) {
                $row[$field] = json_decode($row[$field . '_json'], true) ?: array();
                unset($row[$field . '_json']);
            }
        }
    }
    return $rows;
}

function gic_review_record_contract_revision($contract, $revision, $previous_hash = '') {
    global $wpdb;
    $workspace_id = sanitize_text_field($contract['facts']['workspace']['id'] ?? '');
    $initiative_id = sanitize_text_field($contract['facts']['initiative']['id'] ?? '');
    $record_id = sanitize_text_field($contract['record_id'] ?? '');
    if (!$workspace_id || !$initiative_id || !$record_id) { return; }
    gic_review_ensure_roles($workspace_id);
    $hash = gic_repository_hash($contract);
    $revision_id = gic_review_id('workflow-revision', array('contract',$record_id,$revision,$hash));
    $wpdb->replace(gic_repository_table('workflow_revisions'), array(
        'workflow_revision_id'=>$revision_id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,
        'subject_type'=>'contract','subject_id'=>$record_id,'revision_number'=>(int)$revision,
        'change_type'=>(int)$revision === 1 ? 'create' : 'edit','actor_id'=>(string)get_current_user_id(),
        'summary'=>'Canonical contract repository revision ' . (int)$revision,
        'previous_content_hash'=>sanitize_text_field($previous_hash),'content_hash'=>$hash,
        'snapshot_json'=>wp_json_encode($contract, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
        'created_at'=>current_time('mysql', true),'metadata_json'=>wp_json_encode(array('contract_version'=>$contract['contract_version'] ?? '1.1.0')),
    ));
}

function gic_review_export(WP_REST_Request $request) {
    global $wpdb;
    $workspace_id = sanitize_text_field($request->get_param('workspace_id') ?? '');
    if (!$workspace_id) { return new WP_Error('gic_workspace_required','workspace_id is required.',array('status'=>400)); }
    gic_review_ensure_roles($workspace_id);
    $roles = gic_review_decode_rows(gic_repository_table('workflow_roles'), $workspace_id, array('permissions','metadata'));
    $assignments = gic_review_decode_rows(gic_repository_table('review_assignments'), $workspace_id, array('metadata'));
    $comments = gic_review_decode_rows(gic_repository_table('review_comments'), $workspace_id, array('metadata'));
    $assessments = gic_review_decode_rows(gic_repository_table('quality_assessments'), $workspace_id, array('dimensions','findings','metadata'));
    $decisions = gic_review_decode_rows(gic_repository_table('approval_decisions'), $workspace_id, array('conditions','metadata'));
    $revisions = gic_review_decode_rows(gic_repository_table('workflow_revisions'), $workspace_id, array('snapshot','metadata'));
    $corrections = gic_review_decode_rows(gic_repository_table('correction_records'), $workspace_id, array('proposed_changes','metadata'));
    $publications = gic_review_decode_rows(gic_repository_table('publication_records'), $workspace_id, array('metadata'));
    $events = $wpdb->get_results($wpdb->prepare(
        "SELECT e.* FROM " . gic_repository_table('publication_events') . " e JOIN " . gic_repository_table('publication_records') . " p ON p.publication_id=e.publication_id WHERE p.workspace_id=%s ORDER BY e.event_at",
        $workspace_id
    ), ARRAY_A);
    foreach ($events as &$event) { $event['details'] = json_decode($event['details_json'], true) ?: array(); unset($event['details_json']); }
    $open_comments = count(array_filter($comments, static function($item){ return $item['resolution_status'] === 'open'; }));
    $open_corrections = count(array_filter($corrections, static function($item){ return $item['status'] === 'open'; }));
    $published_without_gate = array_values(array_map(static function($item){ return $item['publication_id']; }, array_filter($publications, static function($item){ return $item['publication_status']==='published' && (!$item['approved_decision_id'] || !$item['quality_assessment_id']); })));
    return rest_ensure_response(array(
        'workflow_type'=>'global_impact_review_workflow','workflow_version'=>'1.6.0','workspace_id'=>$workspace_id,
        'generated_at'=>gmdate('c'),'roles'=>$roles,'review_assignments'=>$assignments,'review_comments'=>$comments,
        'quality_assessments'=>$assessments,'approval_decisions'=>$decisions,'revisions'=>$revisions,
        'corrections'=>$corrections,'publications'=>$publications,'publication_events'=>$events,
        'integrity'=>array('valid'=>empty($published_without_gate),'role_count'=>count($roles),'assignment_count'=>count($assignments),
            'comment_count'=>count($comments),'open_comment_count'=>$open_comments,'quality_assessment_count'=>count($assessments),
            'approval_decision_count'=>count($decisions),'revision_count'=>count($revisions),'correction_count'=>count($corrections),
            'open_correction_count'=>$open_corrections,'publication_count'=>count($publications),'broken_decision_ids'=>array(),
            'published_without_gate_ids'=>$published_without_gate),
        'boundary'=>'Workflow approval documents governance decisions; it is not external assurance, certification, or a guarantee that source claims are true.',
    ));
}

function gic_review_assignment_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $workspace_id = sanitize_text_field($data['workspace_id'] ?? '');
    $initiative_id = sanitize_text_field($data['initiative_id'] ?? '');
    $role_id = sanitize_text_field($data['role_id'] ?? '');
    $reviewer_id = sanitize_text_field($data['reviewer_id'] ?? '');
    if (!$workspace_id || !$initiative_id || !$role_id || !$reviewer_id) { return new WP_Error('gic_review_fields','workspace_id, initiative_id, role_id, and reviewer_id are required.',array('status'=>400)); }
    gic_review_ensure_roles($workspace_id);
    if (!$wpdb->get_var($wpdb->prepare("SELECT role_id FROM " . gic_repository_table('workflow_roles') . " WHERE role_id=%s AND workspace_id=%s AND archived_at IS NULL", $role_id, $workspace_id))) {
        return new WP_Error('gic_role_invalid','The review role is not active in this workspace.',array('status'=>400));
    }
    $now = current_time('mysql', true);
    $assignment_id = gic_review_id('review-assignment', array($workspace_id,$initiative_id,$data['subject_type'] ?? 'contract',$data['subject_id'] ?? $initiative_id,$reviewer_id,$role_id,microtime(true)));
    $row = array('assignment_id'=>$assignment_id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,
        'subject_type'=>sanitize_key($data['subject_type'] ?? 'contract'),'subject_id'=>sanitize_text_field($data['subject_id'] ?? $initiative_id),
        'reviewer_id'=>$reviewer_id,'role_id'=>$role_id,'status'=>'pending','priority'=>sanitize_key($data['priority'] ?? 'normal'),
        'due_at'=>!empty($data['due_at']) ? sanitize_text_field($data['due_at']) : null,'assigned_by'=>(string)get_current_user_id(),
        'assigned_at'=>$now,'started_at'=>null,'completed_at'=>null,'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata'] ?? array()));
    $wpdb->insert(gic_repository_table('review_assignments'), $row);
    $row['metadata'] = json_decode($row['metadata_json'], true); unset($row['metadata_json']);
    return rest_ensure_response($row);
}

function gic_review_comment_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $assignment_id = sanitize_text_field($data['assignment_id'] ?? '');
    $body = sanitize_textarea_field($data['body'] ?? '');
    $assignment = $wpdb->get_row($wpdb->prepare("SELECT * FROM " . gic_repository_table('review_assignments') . " WHERE assignment_id=%s", $assignment_id), ARRAY_A);
    if (!$assignment || !$body) { return new WP_Error('gic_comment_invalid','A valid assignment and comment body are required.',array('status'=>400)); }
    $now = current_time('mysql', true);
    $comment_id = gic_review_id('review-comment', array($assignment_id,get_current_user_id(),microtime(true),$body));
    $row = array('comment_id'=>$comment_id,'assignment_id'=>$assignment_id,'workspace_id'=>$assignment['workspace_id'],'initiative_id'=>$assignment['initiative_id'],
        'subject_type'=>$assignment['subject_type'],'subject_id'=>$assignment['subject_id'],'author_id'=>sanitize_text_field($data['author_id'] ?? (string)get_current_user_id()),
        'parent_comment_id'=>sanitize_text_field($data['parent_comment_id'] ?? ''),'visibility'=>sanitize_key($data['visibility'] ?? 'workspace'),
        'body'=>$body,'resolution_status'=>'open','resolved_by'=>'','resolved_at'=>null,'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata'] ?? array()));
    $wpdb->insert(gic_repository_table('review_comments'), $row);
    return rest_ensure_response($row);
}

function gic_review_quality_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params();
    $dimensions = is_array($data['dimensions'] ?? null) ? $data['dimensions'] : array();
    $weighted = 0.0; $maximum = 0.0; $clean = array();
    foreach ($dimensions as $dimension) {
        $score = (float)($dimension['score'] ?? 0); $max = (float)($dimension['maximum_score'] ?? 100); $weight = (float)($dimension['weight'] ?? 1);
        if ($max <= 0 || $weight <= 0 || $score < 0 || $score > $max) { return new WP_Error('gic_quality_invalid','Quality dimensions contain invalid scores.',array('status'=>400)); }
        $weighted += $score * $weight; $maximum += $max * $weight;
        $clean[] = array('key'=>sanitize_key($dimension['key'] ?? 'dimension'),'score'=>$score,'maximum_score'=>$max,'weight'=>$weight,'finding'=>sanitize_textarea_field($dimension['finding'] ?? ''));
    }
    if (!$clean) { return new WP_Error('gic_quality_required','At least one quality dimension is required.',array('status'=>400)); }
    $score = round(($weighted / $maximum) * 100, 2);
    $grade = $score >= 90 ? 'excellent' : ($score >= 75 ? 'strong' : ($score >= 60 ? 'adequate' : 'weak'));
    $workspace_id = sanitize_text_field($data['workspace_id'] ?? ''); $initiative_id = sanitize_text_field($data['initiative_id'] ?? '');
    $assignment_id = sanitize_text_field($data['assignment_id'] ?? '');
    $assignment = $assignment_id ? $wpdb->get_row($wpdb->prepare("SELECT * FROM " . gic_repository_table('review_assignments') . " WHERE assignment_id=%s", $assignment_id), ARRAY_A) : null;
    $subject_type = $assignment ? $assignment['subject_type'] : sanitize_key($data['subject_type'] ?? 'contract');
    $subject_id = $assignment ? $assignment['subject_id'] : sanitize_text_field($data['subject_id'] ?? $initiative_id);
    $now = current_time('mysql', true); $assessor = sanitize_text_field($data['assessor_id'] ?? (string)get_current_user_id());
    $assessment_id = gic_review_id('quality-assessment', array($workspace_id,$initiative_id,$subject_type,$subject_id,$assessor,microtime(true)));
    $row = array('assessment_id'=>$assessment_id,'assignment_id'=>$assignment_id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,
        'subject_type'=>$subject_type,'subject_id'=>$subject_id,'rubric_id'=>sanitize_text_field($data['rubric_id'] ?? 'gic-core-quality'),
        'rubric_version'=>sanitize_text_field($data['rubric_version'] ?? '1.0'),'assessor_id'=>$assessor,'status'=>'submitted','score'=>$score,
        'maximum_score'=>100,'grade'=>$grade,'dimensions_json'=>wp_json_encode($clean),'findings_json'=>wp_json_encode($data['findings'] ?? array()),
        'limitations'=>sanitize_textarea_field($data['limitations'] ?? ''),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'submitted_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata'] ?? array()));
    $wpdb->insert(gic_repository_table('quality_assessments'), $row);
    $row['dimensions']=$clean; unset($row['dimensions_json']);
    return rest_ensure_response($row);
}

function gic_review_decision_rest(WP_REST_Request $request) {
    global $wpdb;
    $data = $request->get_json_params(); $assignment_id = sanitize_text_field($data['assignment_id'] ?? '');
    $decision = sanitize_key($data['decision'] ?? '');
    if (!in_array($decision,array('approve','request_changes','reject','abstain'),true)) { return new WP_Error('gic_decision_invalid','Unsupported review decision.',array('status'=>400)); }
    $assignment = $wpdb->get_row($wpdb->prepare("SELECT * FROM " . gic_repository_table('review_assignments') . " WHERE assignment_id=%s", $assignment_id), ARRAY_A);
    if (!$assignment) { return new WP_Error('gic_assignment_missing','Review assignment not found.',array('status'=>404)); }
    if ($decision === 'approve') {
        $open = (int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM " . gic_repository_table('review_comments') . " WHERE assignment_id=%s AND resolution_status='open'", $assignment_id));
        $score = $wpdb->get_var($wpdb->prepare("SELECT score FROM " . gic_repository_table('quality_assessments') . " WHERE assignment_id=%s AND status='submitted' ORDER BY created_at DESC LIMIT 1", $assignment_id));
        if ($open) { return new WP_Error('gic_open_comments','Approval is blocked while comments remain open.',array('status'=>409)); }
        if ($score === null || (float)$score < 60) { return new WP_Error('gic_quality_gate','Approval requires an adequate submitted quality assessment.',array('status'=>409)); }
    }
    $now = current_time('mysql', true); $reviewer = sanitize_text_field($data['reviewer_id'] ?? $assignment['reviewer_id']);
    $decision_id = gic_review_id('approval-decision', array($assignment_id,$reviewer,$decision,microtime(true)));
    $prior = (string)$wpdb->get_var($wpdb->prepare("SELECT decision_id FROM " . gic_repository_table('approval_decisions') . " WHERE assignment_id=%s ORDER BY decided_at DESC LIMIT 1", $assignment_id));
    $row = array('decision_id'=>$decision_id,'assignment_id'=>$assignment_id,'workspace_id'=>$assignment['workspace_id'],'initiative_id'=>$assignment['initiative_id'],
        'subject_type'=>$assignment['subject_type'],'subject_id'=>$assignment['subject_id'],'reviewer_id'=>$reviewer,'decision'=>$decision,
        'rationale'=>sanitize_textarea_field($data['rationale'] ?? ''),'conditions_json'=>wp_json_encode($data['conditions'] ?? array()),
        'decided_at'=>$now,'supersedes_decision_id'=>$prior,'revision'=>1,'metadata_json'=>wp_json_encode($data['metadata'] ?? array()));
    $wpdb->insert(gic_repository_table('approval_decisions'), $row);
    $status = array('approve'=>'approved','request_changes'=>'changes_requested','reject'=>'rejected','abstain'=>'in_review')[$decision];
    $wpdb->update(gic_repository_table('review_assignments'),array('status'=>$status,'completed_at'=>in_array($status,array('approved','rejected'),true)?$now:null,'revision'=>(int)$assignment['revision']+1,'updated_at'=>$now),array('assignment_id'=>$assignment_id));
    return rest_ensure_response($row);
}

function gic_review_correction_rest(WP_REST_Request $request) {
    global $wpdb; $data=$request->get_json_params();
    $workspace_id=sanitize_text_field($data['workspace_id']??''); $initiative_id=sanitize_text_field($data['initiative_id']??''); $reason=sanitize_textarea_field($data['reason']??'');
    if(!$workspace_id||!$initiative_id||!$reason){return new WP_Error('gic_correction_fields','workspace_id, initiative_id, and reason are required.',array('status'=>400));}
    $now=current_time('mysql',true); $subject_type=sanitize_key($data['subject_type']??'contract'); $subject_id=sanitize_text_field($data['subject_id']??$initiative_id);
    $id=gic_review_id('correction',array($workspace_id,$initiative_id,$subject_type,$subject_id,microtime(true),$reason));
    $row=array('correction_id'=>$id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,'subject_type'=>$subject_type,'subject_id'=>$subject_id,
        'severity'=>sanitize_key($data['severity']??'minor'),'status'=>'open','reason'=>$reason,'proposed_changes_json'=>wp_json_encode($data['proposed_changes']??array()),
        'opened_by'=>(string)get_current_user_id(),'opened_at'=>$now,'applied_by'=>'','applied_at'=>null,'resulting_revision_id'=>'','resolution_notes'=>'','revision'=>1,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata']??array()));
    $wpdb->insert(gic_repository_table('correction_records'),$row); return rest_ensure_response($row);
}

function gic_review_contract_row($subject_id, $initiative_id = '') {
    global $wpdb; $table=gic_repository_table('contracts');
    $row=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE record_id=%s",$subject_id),ARRAY_A);
    if(!$row && $initiative_id){$row=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE initiative_id=%s",$initiative_id),ARRAY_A);} return $row;
}

function gic_review_publication_event($publication_id,$type,$reason='',$details=array()){
    global $wpdb; $now=current_time('mysql',true); $id=gic_review_id('publication-event',array($publication_id,$type,microtime(true),$reason));
    $wpdb->insert(gic_repository_table('publication_events'),array('publication_event_id'=>$id,'publication_id'=>$publication_id,'event_type'=>$type,'actor_id'=>(string)get_current_user_id(),'reason'=>$reason,'event_at'=>$now,'details_json'=>wp_json_encode($details)));
}

function gic_review_publication_rest(WP_REST_Request $request) {
    global $wpdb; $data=$request->get_json_params();
    $workspace_id=sanitize_text_field($data['workspace_id']??''); $initiative_id=sanitize_text_field($data['initiative_id']??'');
    $subject_type=sanitize_key($data['subject_type']??'contract'); $subject_id=sanitize_text_field($data['subject_id']??$initiative_id); $title=sanitize_text_field($data['title']??'');
    if(!$workspace_id||!$initiative_id||!$title){return new WP_Error('gic_publication_fields','workspace_id, initiative_id, and title are required.',array('status'=>400));}
    $contract=gic_review_contract_row($subject_id,$initiative_id); if(!$contract){return new WP_Error('gic_subject_missing','Publication subject not found.',array('status'=>404));}
    $now=current_time('mysql',true); $id=gic_review_id('publication',array($workspace_id,$initiative_id,$subject_type,$subject_id,$title,microtime(true)));
    $row=array('publication_id'=>$id,'workspace_id'=>$workspace_id,'initiative_id'=>$initiative_id,'subject_type'=>$subject_type,'subject_id'=>$subject_id,'title'=>$title,
        'publication_status'=>'draft','release_label'=>sanitize_text_field($data['release_label']??''),'public_url'=>esc_url_raw($data['public_url']??''),'approved_decision_id'=>'','quality_assessment_id'=>'',
        'content_hash'=>$contract['content_hash'],'published_revision_id'=>'','published_at'=>null,'published_by'=>'','withdrawn_at'=>null,'withdrawn_by'=>'','withdrawal_reason'=>'',
        'supersedes_publication_id'=>sanitize_text_field($data['supersedes_publication_id']??''),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode($data['metadata']??array()));
    $wpdb->insert(gic_repository_table('publication_records'),$row); gic_review_publication_event($id,'created','',array('content_hash'=>$contract['content_hash'])); return rest_ensure_response($row);
}

function gic_review_publish_rest(WP_REST_Request $request) {
    global $wpdb; $id=sanitize_text_field($request['publication_id']); $table=gic_repository_table('publication_records');
    $publication=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE publication_id=%s",$id),ARRAY_A); if(!$publication){return new WP_Error('gic_publication_missing','Publication not found.',array('status'=>404));}
    if($publication['publication_status']!=='draft'){return new WP_Error('gic_publication_state','Only draft publications can be published.',array('status'=>409));}
    $decision=$wpdb->get_row($wpdb->prepare("SELECT * FROM ".gic_repository_table('approval_decisions')." WHERE subject_type=%s AND subject_id=%s AND decision='approve' ORDER BY decided_at DESC LIMIT 1",$publication['subject_type'],$publication['subject_id']),ARRAY_A);
    $assessment=$wpdb->get_row($wpdb->prepare("SELECT * FROM ".gic_repository_table('quality_assessments')." WHERE subject_type=%s AND subject_id=%s AND status='submitted' AND score>=60 ORDER BY submitted_at DESC LIMIT 1",$publication['subject_type'],$publication['subject_id']),ARRAY_A);
    $open=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM ".gic_repository_table('correction_records')." WHERE subject_type=%s AND subject_id=%s AND status='open'",$publication['subject_type'],$publication['subject_id']));
    if(!$decision||!$assessment){return new WP_Error('gic_publication_gate','Publication requires approval and an adequate quality assessment.',array('status'=>409));}
    if($open){return new WP_Error('gic_publication_corrections','Publication is blocked while corrections remain open.',array('status'=>409));}
    $contract=gic_review_contract_row($publication['subject_id'],$publication['initiative_id']); if(!$contract||!hash_equals($publication['content_hash'],$contract['content_hash'])){return new WP_Error('gic_publication_stale','Publication content changed after the draft was created.',array('status'=>409));}
    $revision_id=(string)$wpdb->get_var($wpdb->prepare("SELECT workflow_revision_id FROM ".gic_repository_table('workflow_revisions')." WHERE subject_type=%s AND subject_id=%s AND content_hash=%s ORDER BY revision_number DESC LIMIT 1",$publication['subject_type'],$publication['subject_id'],$publication['content_hash']));
    $now=current_time('mysql',true); $wpdb->update($table,array('publication_status'=>'published','approved_decision_id'=>$decision['decision_id'],'quality_assessment_id'=>$assessment['assessment_id'],'published_revision_id'=>$revision_id,'published_at'=>$now,'published_by'=>(string)get_current_user_id(),'revision'=>(int)$publication['revision']+1,'updated_at'=>$now),array('publication_id'=>$id));
    gic_review_publication_event($id,'published','',array('decision_id'=>$decision['decision_id'],'assessment_id'=>$assessment['assessment_id'])); return rest_ensure_response($wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE publication_id=%s",$id),ARRAY_A));
}

function gic_review_withdraw_rest(WP_REST_Request $request) {
    global $wpdb; $id=sanitize_text_field($request['publication_id']); $reason=sanitize_textarea_field(($request->get_json_params()['reason']??'')); $table=gic_repository_table('publication_records');
    $publication=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE publication_id=%s",$id),ARRAY_A); if(!$publication||$publication['publication_status']!=='published'||!$reason){return new WP_Error('gic_withdraw_invalid','A published record and withdrawal reason are required.',array('status'=>400));}
    $now=current_time('mysql',true); $wpdb->update($table,array('publication_status'=>'withdrawn','withdrawn_at'=>$now,'withdrawn_by'=>(string)get_current_user_id(),'withdrawal_reason'=>$reason,'revision'=>(int)$publication['revision']+1,'updated_at'=>$now),array('publication_id'=>$id));
    gic_review_publication_event($id,'withdrawn',$reason); return rest_ensure_response($wpdb->get_row($wpdb->prepare("SELECT * FROM {$table} WHERE publication_id=%s",$id),ARRAY_A));
}

function gic_review_register_routes() {
    register_rest_route('global-impact-catalyst/v1','/review-workflow',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_review_export','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/review-assignments',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_assignment_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/review-comments',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_comment_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/quality-assessments',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_quality_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/approval-decisions',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_decision_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/corrections',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_correction_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/publications',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_publication_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/publications/(?P<publication_id>[A-Za-z0-9_-]+)/publish',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_publish_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/publications/(?P<publication_id>[A-Za-z0-9_-]+)/withdraw',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_review_withdraw_rest','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init','gic_review_register_routes');

function gic_review_workflow_shortcode($atts = array()) {
    if (!is_user_logged_in() || !current_user_can('edit_posts')) { return '<p class="gic-review__login">Sign in with editing access to use the review and publication workflow.</p>'; }
    wp_enqueue_style('global-impact-catalyst-review'); wp_enqueue_script('global-impact-catalyst-review');
    ob_start(); ?>
    <section class="gic-review" data-gic-review data-rest="<?php echo esc_url(rest_url('global-impact-catalyst/v1/')); ?>" data-nonce="<?php echo esc_attr(wp_create_nonce('wp_rest')); ?>">
      <header class="gic-review__header"><div><p class="gic-review__eyebrow">Governed review workflow · v1.6.0</p><h2>Review, Quality, and Publication</h2><p>Assign reviewers, document findings, score quality, approve exact revisions, and retain publication or withdrawal history.</p></div><p class="gic-review__boundary">Internal approval is not external assurance, certification, audit, causal proof, or source-truth verification.</p></header>
      <div class="gic-review__cards"><div class="gic-review__card"><span>Assignments</span><strong data-gic-review-count="assignments">0</strong></div><div class="gic-review__card"><span>Open items</span><strong data-gic-review-count="open">0</strong></div><div class="gic-review__card"><span>Publications</span><strong data-gic-review-count="publications">0</strong></div></div>
      <div class="gic-review__grid">
        <div class="gic-review__panel"><h3>Workflow context</h3><div class="gic-review__form"><label class="gic-review__field gic-review__field--wide">Workspace ID<input name="workspace_id" type="text"></label><label class="gic-review__field gic-review__field--wide">Initiative ID<input name="initiative_id" type="text"></label><div class="gic-review__actions gic-review__field--wide"><button type="button" data-gic-review-load>Load workflow</button></div></div><div class="gic-review__status" data-gic-review-status role="status" aria-live="polite">Enter a workspace ID.</div><div class="gic-review__list" data-gic-review-list><p class="gic-review__empty">No workflow loaded.</p></div></div>
        <div class="gic-review__panel"><h3>Assign review</h3><form class="gic-review__form" data-gic-review-assignment><input name="workspace_id" type="hidden"><input name="initiative_id" type="hidden"><label class="gic-review__field gic-review__field--wide">Contract record ID<input name="subject_id" required></label><label class="gic-review__field">Reviewer ID<input name="reviewer_id" required></label><label class="gic-review__field">Role ID<input name="role_id" required></label><label class="gic-review__field">Priority<select name="priority"><option>normal</option><option>high</option><option>urgent</option><option>low</option></select></label><div class="gic-review__actions gic-review__field--wide"><button type="submit">Create assignment</button></div></form><h3>Quality assessment</h3><form class="gic-review__form" data-gic-review-assessment><input name="workspace_id" type="hidden"><input name="initiative_id" type="hidden"><label class="gic-review__field gic-review__field--wide">Assignment ID<input name="assignment_id" required></label><label class="gic-review__field gic-review__field--wide">Assessor ID<input name="assessor_id" required></label><label class="gic-review__field">Evidence score<input name="evidence_score" type="number" min="0" max="100" value="80"></label><label class="gic-review__field">Method score<input name="method_score" type="number" min="0" max="100" value="80"></label><label class="gic-review__field">Traceability score<input name="traceability_score" type="number" min="0" max="100" value="80"></label><div class="gic-review__actions gic-review__field--wide"><button type="submit">Save assessment</button></div></form></div>
      </div>
    </section>
    <script>document.addEventListener('input',function(e){var root=e.target.closest('[data-gic-review]');if(!root)return;if(e.target.name==='workspace_id'||e.target.name==='initiative_id'){root.querySelectorAll('input[type="hidden"][name="'+e.target.name+'"]').forEach(function(input){input.value=e.target.value;});}});</script>
    <?php return ob_get_clean();
}
add_shortcode('global_impact_catalyst_review_workflow','gic_review_workflow_shortcode');


/** Governed trends, comparisons, scenarios, and uncertainty introduced in v1.7.0. */
function gic_analysis_id($kind, $parts = array()) { return 'gic-' . $kind . '-' . substr(hash('sha256', wp_json_encode($parts)), 0, 20); }
function gic_analysis_decode_rows($table, $workspace_id, $json_fields = array()) {
    global $wpdb; $rows=$wpdb->get_results($wpdb->prepare("SELECT * FROM {$table} WHERE workspace_id=%s ORDER BY 1",$workspace_id),ARRAY_A);
    foreach($rows as &$row){foreach($json_fields as $field){$row[$field]=json_decode($row[$field]?:'{}',true);}} return $rows;
}
function gic_analysis_repository(WP_REST_Request $request) {
    $workspace=sanitize_text_field($request->get_param('workspace_id')); if(!$workspace){return new WP_Error('gic_analysis_workspace','workspace_id is required.',array('status'=>400));}
    $benchmarks=gic_analysis_decode_rows(gic_repository_table('analysis_benchmarks'),$workspace,array('metadata_json'));
    $sets=gic_analysis_decode_rows(gic_repository_table('analysis_comparison_sets'),$workspace,array('policy_json','metadata_json'));
    $scenarios=gic_analysis_decode_rows(gic_repository_table('analysis_scenarios'),$workspace,array('parameters_json','assumptions_json','limitations_json','metadata_json'));
    $uncertainty=gic_analysis_decode_rows(gic_repository_table('analysis_uncertainty_models'),$workspace,array('assumptions_json','limitations_json','metadata_json'));
    $runs=gic_analysis_decode_rows(gic_repository_table('analysis_runs'),$workspace,array('result_json','metadata_json'));
    return rest_ensure_response(array('repository_type'=>'global_impact_analysis_repository','repository_version'=>'1.7.0','workspace_id'=>$workspace,'generated_at'=>gmdate('c'),'benchmarks'=>$benchmarks,'comparison_sets'=>$sets,'scenarios'=>$scenarios,'uncertainty_models'=>$uncertainty,'analysis_runs'=>$runs,'sensitivity_runs'=>gic_analysis_decode_rows(gic_repository_table('analysis_sensitivity_runs'),$workspace,array('metadata_json')),'integrity'=>array('valid'=>true,'benchmark_count'=>count($benchmarks),'comparison_set_count'=>count($sets),'scenario_count'=>count($scenarios),'uncertainty_model_count'=>count($uncertainty),'analysis_run_count'=>count($runs)),'boundary'=>'Analysis is descriptive and conditional, not assurance, certification, causal proof, or a verified forecast.'));
}
function gic_analysis_benchmark_rest(WP_REST_Request $request) { global $wpdb; $p=$request->get_json_params(); foreach(array('workspace_id','indicator_id','name','value','unit_id') as $key){if(!isset($p[$key])||$p[$key]===''){return new WP_Error('gic_analysis_required',$key.' is required.',array('status'=>400));}} $id=gic_analysis_id('benchmark',array($p['workspace_id'],$p['indicator_id'],$p['name'],$p['period_label']??'')); $now=current_time('mysql',true); $wpdb->replace(gic_repository_table('analysis_benchmarks'),array('benchmark_id'=>$id,'workspace_id'=>sanitize_text_field($p['workspace_id']),'indicator_id'=>sanitize_text_field($p['indicator_id']),'name'=>sanitize_text_field($p['name']),'value'=>(float)$p['value'],'unit_id'=>sanitize_text_field($p['unit_id']),'period_label'=>sanitize_text_field($p['period_label']??''),'geography'=>sanitize_text_field($p['geography']??''),'population'=>sanitize_text_field($p['population']??''),'quality_status'=>sanitize_text_field($p['quality_status']??'not_assessed'),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>'{}')); return rest_ensure_response(array('benchmark_id'=>$id)); }
function gic_analysis_uncertainty_rest(WP_REST_Request $request) { global $wpdb; $p=$request->get_json_params(); $id=gic_analysis_id('uncertainty',array($p['workspace_id']??'',$p['name']??'',$p['uncertainty_type']??'')); $now=current_time('mysql',true); $wpdb->replace(gic_repository_table('analysis_uncertainty_models'),array('uncertainty_model_id'=>$id,'workspace_id'=>sanitize_text_field($p['workspace_id']??''),'name'=>sanitize_text_field($p['name']??'Uncertainty model'),'uncertainty_type'=>sanitize_text_field($p['uncertainty_type']??'relative'),'absolute_margin'=>isset($p['absolute_margin'])?(float)$p['absolute_margin']:null,'relative_margin_percent'=>isset($p['relative_margin_percent'])?(float)$p['relative_margin_percent']:null,'lower_bound'=>isset($p['lower_bound'])?(float)$p['lower_bound']:null,'upper_bound'=>isset($p['upper_bound'])?(float)$p['upper_bound']:null,'confidence_level'=>(float)($p['confidence_level']??.95),'distribution'=>sanitize_text_field($p['distribution']??'bounded'),'assumptions_json'=>wp_json_encode($p['assumptions']??array()),'limitations_json'=>wp_json_encode($p['limitations']??array()),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>'{}')); return rest_ensure_response(array('uncertainty_model_id'=>$id)); }
function gic_analysis_scenario_rest(WP_REST_Request $request) { global $wpdb; $p=$request->get_json_params(); $id=gic_analysis_id('scenario',array($p['workspace_id']??'',$p['initiative_id']??'',$p['name']??'')); $now=current_time('mysql',true); $wpdb->replace(gic_repository_table('analysis_scenarios'),array('scenario_id'=>$id,'workspace_id'=>sanitize_text_field($p['workspace_id']??''),'initiative_id'=>sanitize_text_field($p['initiative_id']??''),'indicator_id'=>sanitize_text_field($p['indicator_id']??''),'name'=>sanitize_text_field($p['name']??'Scenario'),'model_type'=>sanitize_text_field($p['model_type']??'linear'),'periods'=>max(1,(int)($p['periods']??1)),'base_value'=>isset($p['base_value'])?(float)$p['base_value']:null,'unit_id'=>sanitize_text_field($p['unit_id']??'count'),'parameters_json'=>wp_json_encode($p['parameters']??array()),'assumptions_json'=>wp_json_encode($p['assumptions']??array()),'limitations_json'=>wp_json_encode($p['limitations']??array()),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>'{}')); return rest_ensure_response(array('scenario_id'=>$id)); }
function gic_analysis_trend_rest(WP_REST_Request $request) { return rest_ensure_response(array('analysis_type'=>'trend','analysis_version'=>'1.7.0','workspace_id'=>sanitize_text_field($request->get_param('workspace_id')),'initiative_id'=>sanitize_text_field($request->get_param('initiative_id')),'indicator_id'=>sanitize_text_field($request->get_param('indicator_id')),'integrity'=>array('valid'=>true,'warnings'=>array()),'boundary'=>'Use the Python repository for governed observation selection and persisted trend statistics.')); }
function gic_analysis_comparison_set_rest(WP_REST_Request $request) { global $wpdb; $p=$request->get_json_params(); $id=gic_analysis_id('comparison-set',array($p['workspace_id']??'',$p['indicator_id']??'',$p['name']??'')); $now=current_time('mysql',true); $wpdb->replace(gic_repository_table('analysis_comparison_sets'),array('comparison_set_id'=>$id,'workspace_id'=>sanitize_text_field($p['workspace_id']??''),'indicator_id'=>sanitize_text_field($p['indicator_id']??''),'name'=>sanitize_text_field($p['name']??'Comparison set'),'policy_json'=>wp_json_encode($p['comparison_policy']??array()),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>'{}')); return rest_ensure_response(array('comparison_set_id'=>$id)); }
function gic_analysis_sensitivity_rest(WP_REST_Request $request) { $p=$request->get_json_params(); return rest_ensure_response(array('analysis_type'=>'sensitivity','analysis_version'=>'1.7.0','scenario_id'=>sanitize_text_field($p['scenario_id']??''),'parameter_ranges'=>$p['parameter_ranges']??array(),'boundary'=>'Sensitivity ranks mathematical responsiveness, not causal importance.')); }
function gic_analysis_register_routes() {
    register_rest_route('global-impact-catalyst/v1','/analysis-repository',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_analysis_repository','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/analysis-benchmarks',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_analysis_benchmark_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/analysis-uncertainty-models',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_analysis_uncertainty_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/analysis-scenarios',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_analysis_scenario_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/analysis-trends',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_analysis_trend_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/analysis-comparison-sets',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_analysis_comparison_set_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/analysis-sensitivity',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_analysis_sensitivity_rest','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init','gic_analysis_register_routes');
function gic_analysis_studio_shortcode($atts=array()) {
    if(!is_user_logged_in()||!current_user_can('edit_posts')){return '<p class="gic-analysis__login">Sign in with editing access to use the Analysis Studio.</p>';}
    wp_enqueue_style('global-impact-catalyst-analysis'); wp_enqueue_script('global-impact-catalyst-analysis');
    ob_start(); ?>
    <section class="gic-analysis" data-gic-analysis-studio data-rest="<?php echo esc_url(rest_url('global-impact-catalyst/v1/')); ?>" data-nonce="<?php echo esc_attr(wp_create_nonce('wp_rest')); ?>">
      <header class="gic-analysis__header"><div><p class="gic-analysis__eyebrow">Governed analysis · v1.7.0</p><h2>Trends, Comparisons, Scenarios, and Uncertainty</h2><p>Build transparent analytical records over governed observations, targets, units, methods, evidence, and review state.</p></div><p class="gic-analysis__boundary">Conditional and descriptive analysis only—not assurance, certification, causal proof, or a verified forecast.</p></header>
      <div class="gic-analysis__grid"><div class="gic-analysis__panel"><h3>Analysis context</h3><label>Workspace ID<input name="workspace_id"></label><label>Initiative ID<input name="initiative_id"></label><label>Indicator ID<input name="indicator_id"></label><div class="gic-analysis__actions"><button type="button" data-gic-analysis-load>Load repository</button><button type="button" data-gic-analysis-trend>Run trend</button></div></div>
      <div class="gic-analysis__panel"><h3>Create governed records</h3><div class="gic-analysis__actions"><button type="button" data-gic-analysis-benchmark>Add benchmark</button><button type="button" data-gic-analysis-uncertainty>Add uncertainty</button><button type="button" data-gic-analysis-scenario>Add scenario</button></div><pre data-gic-analysis-results aria-live="polite">Enter repository identifiers to begin.</pre></div></div>
    </section><?php return ob_get_clean();
}
add_shortcode('global_impact_catalyst_analysis_studio','gic_analysis_studio_shortcode');

/** Reporting, Publication, and Reproducible Export Studio — v1.8.0. */
function gic_reporting_id($kind,$parts=array()){return 'gic-'.$kind.'-'.substr(hash('sha256',wp_json_encode($parts,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)),0,20);}
function gic_reporting_rows($table,$workspace,$json_fields=array()){
    global $wpdb;
    $rows=$wpdb->get_results($wpdb->prepare('SELECT * FROM '.$table.' WHERE workspace_id=%s ORDER BY updated_at DESC',$workspace),ARRAY_A);
    foreach($rows as &$row){foreach($json_fields as $field){$name=preg_replace('/_json$/','',$field);$row[$name]=json_decode($row[$field]??'{}',true);unset($row[$field]);}}
    return $rows;
}
function gic_reporting_repository_rest(WP_REST_Request $request){
    global $wpdb;
    $w=sanitize_text_field($request->get_param('workspace_id'));
    $templates=gic_reporting_rows(gic_repository_table('report_templates'),$w,array('sections_json','accessibility_json','metadata_json'));
    $reports=gic_reporting_rows(gic_repository_table('report_documents'),$w,array('document_json','citations_json','methodology_json','metadata_json'));
    $dashboards=gic_reporting_rows(gic_repository_table('dashboard_definitions'),$w,array('layout_json','metadata_json'));
    foreach($dashboards as &$d){
        $cards=$wpdb->get_results($wpdb->prepare('SELECT * FROM '.gic_repository_table('dashboard_cards').' WHERE dashboard_id=%s ORDER BY position,title',$d['dashboard_id']),ARRAY_A);
        foreach($cards as &$c){$c['configuration']=json_decode($c['configuration_json']??'{}',true);$c['metadata']=json_decode($c['metadata_json']??'{}',true);unset($c['configuration_json'],$c['metadata_json']);}
        $d['cards']=$cards;
    }
    $snapshots=$wpdb->get_results($wpdb->prepare('SELECT * FROM '.gic_repository_table('publication_snapshots').' WHERE workspace_id=%s ORDER BY created_at',$w),ARRAY_A);
    foreach($snapshots as &$snapshot){$snapshot['snapshot']=json_decode($snapshot['snapshot_json']??'{}',true);$snapshot['metadata']=json_decode($snapshot['metadata_json']??'{}',true);unset($snapshot['snapshot_json'],$snapshot['metadata_json']);}
    $bundles=$wpdb->get_results($wpdb->prepare('SELECT * FROM '.gic_repository_table('export_bundles').' WHERE workspace_id=%s ORDER BY created_at',$w),ARRAY_A);
    $checksum_failures=array();$count_failures=array();
    foreach($bundles as &$bundle){
        $bundle['metadata']=json_decode($bundle['metadata_json']??'{}',true);unset($bundle['metadata_json']);
        $artifacts=$wpdb->get_results($wpdb->prepare('SELECT * FROM '.gic_repository_table('export_artifacts').' WHERE export_bundle_id=%s ORDER BY artifact_path',$bundle['export_bundle_id']),ARRAY_A);
        foreach($artifacts as &$artifact){
            $artifact['metadata']=json_decode($artifact['metadata_json']??'{}',true);unset($artifact['metadata_json']);
            if(hash('sha256',$artifact['content_text'])!==$artifact['sha256']){$checksum_failures[]=$artifact['artifact_id'];}
        }
        if(count($artifacts)!==(int)$bundle['artifact_count']){$count_failures[]=$bundle['export_bundle_id'];}
        $bundle['artifacts']=$artifacts;
    }
    return rest_ensure_response(array(
        'repository_type'=>'global_impact_reporting_repository','repository_version'=>'1.8.0','workspace_id'=>$w,'generated_at'=>gmdate('c'),
        'report_templates'=>$templates,'reports'=>$reports,'dashboards'=>$dashboards,'publication_snapshots'=>$snapshots,'export_bundles'=>$bundles,
        'integrity'=>array('valid'=>!$checksum_failures&&!$count_failures,'template_count'=>count($templates),'report_count'=>count($reports),'dashboard_count'=>count($dashboards),'publication_snapshot_count'=>count($snapshots),'export_bundle_count'=>count($bundles),'artifact_checksum_failures'=>$checksum_failures,'bundle_count_failures'=>$count_failures),
        'boundary'=>'Reporting integrity is not assurance, certification, audit, or causal proof.'
    ));
}
function gic_reporting_template_rest(WP_REST_Request $request){
    global $wpdb;$p=$request->get_json_params();$workspace=sanitize_text_field($p['workspace_id']??'');$name=sanitize_text_field($p['name']??'');
    if(!$workspace||!$name)return new WP_Error('gic_reporting_required','workspace_id and name are required.',array('status'=>400));
    $id=sanitize_text_field($p['template_id']??gic_reporting_id('report-template',array($workspace,$name)));$existing=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.gic_repository_table('report_templates').' WHERE template_id=%s',$id),ARRAY_A);$now=current_time('mysql',true);
    $wpdb->replace(gic_repository_table('report_templates'),array('template_id'=>$id,'workspace_id'=>$workspace,'name'=>$name,'report_type'=>sanitize_key($p['report_type']??'impact_report'),'sections_json'=>wp_json_encode((array)($p['sections']??array('executive_summary','results','methodology','limitations','references'))),'citation_style'=>sanitize_key($p['citation_style']??'harvard'),'accessibility_json'=>wp_json_encode((array)($p['accessibility_profile']??array('wcag_target'=>'2.2 AA','heading_order'=>true,'text_alternatives'=>true))),'revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>wp_json_encode((array)($p['metadata']??array()))));
    return rest_ensure_response(array('template_id'=>$id,'revision'=>$existing?((int)$existing['revision']+1):1));
}
function gic_reporting_report_rest(WP_REST_Request $request){
    global $wpdb;$p=$request->get_json_params();foreach(array('workspace_id','initiative_id','title') as $key){if(empty($p[$key]))return new WP_Error('gic_reporting_required',$key.' is required.',array('status'=>400));}
    $contract=$wpdb->get_row($wpdb->prepare('SELECT contract_json,content_hash FROM '.gic_repository_table('contracts').' WHERE initiative_id=%s',sanitize_text_field($p['initiative_id'])),ARRAY_A);if(!$contract)return new WP_Error('gic_reporting_missing','Initiative not found.',array('status'=>404));
    $document=array('report_type'=>'impact_report','title'=>sanitize_text_field($p['title']),'audience'=>sanitize_key($p['audience']??'public'),'period_label'=>sanitize_text_field($p['period_label']??''),'contract'=>json_decode($contract['contract_json'],true),'limitations'=>array('Validation and reporting do not establish assurance or causality.'));
    $hash=hash('sha256',wp_json_encode($document,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE));$id=gic_reporting_id('report',array($p['workspace_id'],$p['initiative_id'],$hash));$existing=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.gic_repository_table('report_documents').' WHERE report_id=%s',$id),ARRAY_A);$now=current_time('mysql',true);
    $markdown='# '.$document['title']."\n\nGoverned Global Impact Catalyst report.\n\n## Methodology appendix\n\n- Canonical contract: v1.1.0\n";
    $html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'.esc_html($document['title']).'</title></head><body><a href="#main">Skip to report</a><main id="main"><h1>'.esc_html($document['title']).'</h1><p>Governed Global Impact Catalyst report.</p><h2>Limitations</h2><p>Validation and reporting do not establish assurance or causality.</p></main></body></html>';
    $wpdb->replace(gic_repository_table('report_documents'),array('report_id'=>$id,'workspace_id'=>sanitize_text_field($p['workspace_id']),'initiative_id'=>sanitize_text_field($p['initiative_id']),'template_id'=>sanitize_text_field($p['template_id']??''),'title'=>$document['title'],'report_type'=>'impact_report','audience'=>$document['audience'],'period_label'=>$document['period_label'],'source_bundle_hash'=>$contract['content_hash'],'content_hash'=>$hash,'document_json'=>wp_json_encode($document),'rendered_markdown'=>$markdown,'rendered_html'=>$html,'citations_json'=>'[]','methodology_json'=>wp_json_encode(array('canonical_contract_version'=>'1.1.0','reporting_version'=>'1.8.0')),'revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>'{}'));
    return rest_ensure_response(array('report_id'=>$id,'content_hash'=>$hash,'rendered_markdown'=>$markdown,'rendered_html'=>$html));
}
function gic_reporting_dashboard_rest(WP_REST_Request $request){
    global $wpdb;$p=$request->get_json_params();if(empty($p['workspace_id']))return new WP_Error('gic_reporting_required','workspace_id is required.',array('status'=>400));
    $id=gic_reporting_id('dashboard',array($p['workspace_id']??'',$p['initiative_id']??'',$p['name']??''));$existing=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.gic_repository_table('dashboard_definitions').' WHERE dashboard_id=%s',$id),ARRAY_A);$now=current_time('mysql',true);
    $wpdb->replace(gic_repository_table('dashboard_definitions'),array('dashboard_id'=>$id,'workspace_id'=>sanitize_text_field($p['workspace_id']??''),'initiative_id'=>sanitize_text_field($p['initiative_id']??''),'name'=>sanitize_text_field($p['name']??'Impact Dashboard'),'audience'=>sanitize_key($p['audience']??'internal'),'layout_json'=>wp_json_encode($p['layout']??array('columns'=>2)),'revision'=>$existing?((int)$existing['revision']+1):1,'created_at'=>$existing['created_at']??$now,'updated_at'=>$now,'metadata_json'=>'{}'));
    return rest_ensure_response(array('dashboard_id'=>$id));
}
function gic_reporting_snapshot_rest(WP_REST_Request $request){
    global $wpdb;$p=$request->get_json_params();$publication_id=sanitize_text_field($p['publication_id']??'');
    $publication=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.gic_repository_table('publication_records').' WHERE publication_id=%s',$publication_id),ARRAY_A);
    if(!$publication||$publication['publication_status']!=='published')return new WP_Error('gic_reporting_publication','A published publication is required.',array('status'=>409));
    $report_id=sanitize_text_field($p['report_id']??'');$report=$report_id?$wpdb->get_row($wpdb->prepare('SELECT report_id,content_hash,title FROM '.gic_repository_table('report_documents').' WHERE report_id=%s',$report_id),ARRAY_A):null;
    $snapshot=array('snapshot_type'=>'global_impact_publication_snapshot','snapshot_version'=>'1.8.0','publication'=>$publication,'report'=>$report,'hashes'=>array('contract_hash'=>$publication['content_hash'],'report_hash'=>$report['content_hash']??''));
    $snapshot_hash=hash('sha256',wp_json_encode($snapshot,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE));$id=gic_reporting_id('publication-snapshot',array($publication_id,$snapshot_hash));$now=current_time('mysql',true);
    $wpdb->replace(gic_repository_table('publication_snapshots'),array('snapshot_id'=>$id,'publication_id'=>$publication_id,'workspace_id'=>$publication['workspace_id'],'initiative_id'=>$publication['initiative_id'],'report_id'=>$report_id,'snapshot_hash'=>$snapshot_hash,'snapshot_json'=>wp_json_encode($snapshot),'created_at'=>$now,'metadata_json'=>'{}'));
    return rest_ensure_response(array('snapshot_id'=>$id,'snapshot_hash'=>$snapshot_hash,'snapshot'=>$snapshot));
}
function gic_reporting_export_rest(WP_REST_Request $request){
    global $wpdb;$p=$request->get_json_params();$workspace=sanitize_text_field($p['workspace_id']??'');if(!$workspace)return new WP_Error('gic_reporting_required','workspace_id is required.',array('status'=>400));
    $report_id=sanitize_text_field($p['report_id']??'');$snapshot_id=sanitize_text_field($p['publication_snapshot_id']??'');$artifacts=array();
    $repository_request=new WP_REST_Request('GET','/');$repository_request->set_param('workspace_id',$workspace);$repository=gic_reporting_repository_rest($repository_request)->get_data();$repository['generated_at']='1980-01-01T00:00:00+00:00';$repository['export_bundles']=array();$repository['integrity']['export_bundle_count']=0;$artifacts['reporting-repository.json']=wp_json_encode($repository,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)."\n";
    if($report_id){$report=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.gic_repository_table('report_documents').' WHERE report_id=%s',$report_id),ARRAY_A);if($report){$artifacts['report/report.md']=$report['rendered_markdown'];$artifacts['report/report.html']=$report['rendered_html'];$artifacts['report/report.json']=$report['document_json'];}}
    if($snapshot_id){$snapshot=$wpdb->get_row($wpdb->prepare('SELECT snapshot_json FROM '.gic_repository_table('publication_snapshots').' WHERE snapshot_id=%s',$snapshot_id),ARRAY_A);if($snapshot)$artifacts['publication-snapshot.json']=$snapshot['snapshot_json'];}
    ksort($artifacts);$manifest_artifacts=array();foreach($artifacts as $path=>$content){$manifest_artifacts[]=array('path'=>$path,'byte_size'=>strlen($content),'sha256'=>hash('sha256',$content));}
    $manifest=array('bundle_type'=>'global_impact_reproducible_export','bundle_version'=>'1.8.0','workspace_id'=>$workspace,'initiative_id'=>sanitize_text_field($p['initiative_id']??''),'report_id'=>$report_id,'publication_snapshot_id'=>$snapshot_id,'artifacts'=>$manifest_artifacts,'reproducibility'=>array('hash_algorithm'=>'sha256','wordpress_artifact_set'=>true),'boundary'=>'Export integrity proves byte identity, not factual truth, assurance, or causal validity.');
    $manifest_text=wp_json_encode($manifest,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)."\n";$artifacts['manifest.json']=$manifest_text;ksort($artifacts);$sums='';foreach($artifacts as $path=>$content){$sums.=hash('sha256',$content).'  '.$path."\n";}$artifacts['SHA256SUMS.txt']=$sums;ksort($artifacts);
    $manifest_hash=hash('sha256',wp_json_encode($manifest,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE));$archive_hash=hash('sha256',implode('',array_map(static function($path)use($artifacts){return $path."\0".$artifacts[$path]."\0";},array_keys($artifacts))));$bundle_id=gic_reporting_id('export-bundle',array($workspace,$manifest_hash));$now=current_time('mysql',true);
    $wpdb->replace(gic_repository_table('export_bundles'),array('export_bundle_id'=>$bundle_id,'workspace_id'=>$workspace,'initiative_id'=>sanitize_text_field($p['initiative_id']??''),'report_id'=>$report_id,'publication_snapshot_id'=>$snapshot_id,'manifest_hash'=>$manifest_hash,'archive_hash'=>$archive_hash,'artifact_count'=>count($artifacts),'created_at'=>$now,'metadata_json'=>wp_json_encode(array('format'=>'wordpress-artifact-set'))));$wpdb->delete(gic_repository_table('export_artifacts'),array('export_bundle_id'=>$bundle_id));
    foreach($artifacts as $path=>$content){$wpdb->insert(gic_repository_table('export_artifacts'),array('artifact_id'=>gic_reporting_id('export-artifact',array($bundle_id,$path)),'export_bundle_id'=>$bundle_id,'artifact_path'=>$path,'media_type'=>(substr($path,-5)==='.html'?'text/html':(substr($path,-3)==='.md'?'text/markdown':(substr($path,-4)==='.txt'?'text/plain':'application/json'))),'byte_size'=>strlen($content),'sha256'=>hash('sha256',$content),'content_text'=>$content,'created_at'=>$now,'metadata_json'=>'{}'));}
    return rest_ensure_response(array('export_bundle_id'=>$bundle_id,'manifest_hash'=>$manifest_hash,'archive_hash'=>$archive_hash,'artifact_count'=>count($artifacts),'manifest'=>$manifest));
}
function gic_reporting_register_routes(){
    register_rest_route('global-impact-catalyst/v1','/reporting-repository',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_reporting_repository_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/report-templates',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_reporting_template_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/reports',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_reporting_report_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/dashboards',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_reporting_dashboard_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/publication-snapshots',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_reporting_snapshot_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/reproducible-exports',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_reporting_export_rest','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init','gic_reporting_register_routes');
function gic_reporting_studio_shortcode($atts=array()){
    if(!is_user_logged_in()||!current_user_can('edit_posts'))return '<p class="gic-reporting__login">Sign in with editing access to use the Reporting Studio.</p>';
    wp_enqueue_style('global-impact-catalyst-reporting');wp_enqueue_script('global-impact-catalyst-reporting');ob_start();?>
<section class="gic-reporting" data-gic-reporting-studio data-rest="<?php echo esc_url(rest_url('global-impact-catalyst/v1/')); ?>" data-nonce="<?php echo esc_attr(wp_create_nonce('wp_rest')); ?>"><header class="gic-reporting__header"><p class="gic-reporting__eyebrow">Governed reporting · v1.8.0</p><h2>Reporting, Publication, and Reproducible Export Studio</h2><p>Create accessible impact reports, methodology appendices, dashboards, publication snapshots, and checksum-governed export bundles.</p><p class="gic-reporting__boundary">Publication and checksum integrity do not constitute assurance, certification, audit, or causal proof.</p></header><div class="gic-reporting__grid"><div class="gic-reporting__panel"><h3>Report context</h3><label>Workspace ID<input name="workspace_id"></label><label>Initiative ID<input name="initiative_id"></label><label>Report title<input name="title" value="Impact Report"></label><label>Period label<input name="period_label"></label><label>Publication ID<input name="publication_id" placeholder="Published publication ID"></label><label>Report ID<input name="report_id" placeholder="Generated report ID"></label><label>Snapshot ID<input name="snapshot_id" placeholder="Publication snapshot ID"></label><div class="gic-reporting__actions"><button type="button" data-gic-reporting-load>Load repository</button><button type="button" data-gic-reporting-template>Create template</button><button type="button" data-gic-reporting-report>Create report</button><button type="button" data-gic-reporting-dashboard>Create dashboard</button><button type="button" data-gic-reporting-snapshot>Create snapshot</button><button type="button" data-gic-reporting-export>Create export</button></div></div><div class="gic-reporting__panel"><h3>Reporting output</h3><pre data-gic-reporting-results aria-live="polite">Enter workspace and initiative identifiers to begin.</pre></div></div></section><?php return ob_get_clean();}
add_shortcode('global_impact_catalyst_reporting_studio','gic_reporting_studio_shortcode');


/* -------------------------------------------------------------------------
 * v1.9.0 — Public API, governed embeds, and Sustainable Catalyst handoffs
 * ---------------------------------------------------------------------- */
function gic_integration_jsonld_context() {
    return array(
        '@version' => 1.1,
        'gic' => 'https://sustainablecatalyst.com/ns/global-impact-catalyst/',
        'schema' => 'https://schema.org/',
        'prov' => 'http://www.w3.org/ns/prov#',
        'name' => 'schema:name',
        'description' => 'schema:description',
        'wasDerivedFrom' => array('@id' => 'prov:wasDerivedFrom', '@type' => '@id'),
    );
}
function gic_integration_boundary() {
    return 'Public records are approved publication views. They are not ESG assurance, SDG certification, audit findings, regulatory filings, factual verification, or causal proof.';
}
function gic_integration_id($kind, $parts) {
    return 'gic-' . sanitize_key($kind) . '-' . substr(hash('sha256', implode('|', array_map('strval', (array) $parts))), 0, 20);
}
function gic_integration_envelope($data, $resource_type, $meta = array()) {
    return array(
        '@context' => gic_integration_jsonld_context(),
        'api_version' => 'v1',
        'data' => $data,
        'meta' => array_merge(array('api_version' => 'v1', 'generated_at' => gmdate('c'), 'resource_type' => $resource_type), $meta),
        'boundary' => gic_integration_boundary(),
    );
}
function gic_integration_public_profile($publication_id) {
    global $wpdb;
    $publication = $wpdb->get_row($wpdb->prepare(
        'SELECT * FROM ' . gic_repository_table('publication_records') . ' WHERE publication_id=%s AND publication_status=%s',
        $publication_id, 'published'
    ), ARRAY_A);
    if (!$publication) { return new WP_Error('gic_publication_not_public', 'The publication is not public.', array('status' => 404)); }
    $snapshot = $wpdb->get_row($wpdb->prepare(
        'SELECT * FROM ' . gic_repository_table('publication_snapshots') . ' WHERE publication_id=%s ORDER BY created_at DESC LIMIT 1',
        $publication_id
    ), ARRAY_A);
    if (!$snapshot) { return new WP_Error('gic_publication_snapshot_required', 'The publication has no approved snapshot.', array('status' => 409)); }
    $contract_row = $wpdb->get_row($wpdb->prepare(
        'SELECT * FROM ' . gic_repository_table('contracts') . ' WHERE initiative_id=%s LIMIT 1',
        $publication['initiative_id']
    ), ARRAY_A);
    if (!$contract_row) { return new WP_Error('gic_contract_missing', 'The approved contract is unavailable.', array('status' => 404)); }
    if (!empty($publication['content_hash']) && !hash_equals((string) $publication['content_hash'], (string) $contract_row['content_hash'])) {
        return new WP_Error('gic_publication_stale', 'The current contract no longer matches the approved publication.', array('status' => 409));
    }
    $contract = json_decode($contract_row['contract_json'], true);
    if (!is_array($contract)) { return new WP_Error('gic_contract_invalid', 'The approved contract cannot be decoded.', array('status' => 500)); }
    $facts = $contract['facts'] ?? array();
    $measurement = $facts['measurement'] ?? array();
    $observations = $measurement['observations'] ?? array();
    $latest = $observations ? end($observations) : array();
    $report = null;
    if (!empty($snapshot['report_id'])) {
        $report_row = $wpdb->get_row($wpdb->prepare('SELECT * FROM ' . gic_repository_table('report_documents') . ' WHERE report_id=%s', $snapshot['report_id']), ARRAY_A);
        if ($report_row) {
            $report = array(
                'report_id' => $report_row['report_id'], 'title' => $report_row['title'],
                'report_type' => $report_row['report_type'], 'audience' => $report_row['audience'],
                'period_label' => $report_row['period_label'], 'content_hash' => $report_row['content_hash'],
                'document' => json_decode($report_row['document_json'], true),
                'rendered_html' => $report_row['rendered_html'], 'rendered_markdown' => $report_row['rendered_markdown'],
                'citations' => json_decode($report_row['citations_json'], true),
                'methodology' => json_decode($report_row['methodology_json'], true),
            );
        }
    }
    return array(
        'publication' => array(
            'publication_id' => $publication['publication_id'], 'title' => $publication['title'],
            'release_label' => $publication['release_label'], 'public_url' => $publication['public_url'],
            'published_at' => $publication['published_at'], 'content_hash' => $publication['content_hash'],
        ),
        'snapshot' => array('snapshot_id' => $snapshot['snapshot_id'], 'snapshot_hash' => $snapshot['snapshot_hash']),
        'initiative' => array(
            'id' => $facts['initiative']['id'] ?? '', 'name' => $facts['initiative']['name'] ?? '',
            'description' => $facts['initiative']['description'] ?? '',
            'goal' => $facts['goal']['statement'] ?? '', 'outcomes' => $facts['outcomes'] ?? array(),
            'geography' => array('name' => $facts['geography']['name'] ?? '', 'type' => $facts['geography']['geography_type'] ?? ''),
            'indicator' => array(
                'id' => $facts['indicator']['id'] ?? '', 'name' => $facts['indicator']['name'] ?? '',
                'definition' => $facts['indicator']['definition'] ?? '', 'direction' => $facts['indicator']['direction'] ?? '',
            ),
            'latest_observation' => array('value' => $latest['value'] ?? null, 'unit' => $latest['unit'] ?? '', 'period' => $latest['period'] ?? ''),
            'baseline' => $measurement['baseline'] ?? null, 'target' => $measurement['target'] ?? null,
            'derived' => $contract['derived'] ?? array(), 'contract_version' => $contract['contract_version'] ?? '1.1.0',
        ),
        'report' => $report,
    );
}
function gic_integration_public_catalog_rest(WP_REST_Request $request) {
    global $wpdb;
    $page = max(1, (int) $request->get_param('page'));
    $size = min(100, max(1, (int) ($request->get_param('page_size') ?: 20)));
    $search = sanitize_text_field($request->get_param('search') ?: '');
    $where = "p.publication_status='published'"; $params = array();
    if ($search !== '') { $where .= ' AND (p.title LIKE %s OR c.contract_json LIKE %s)'; $like = '%' . $wpdb->esc_like($search) . '%'; $params[] = $like; $params[] = $like; }
    $base = ' FROM ' . gic_repository_table('publication_records') . ' p INNER JOIN ' . gic_repository_table('contracts') . " c ON c.initiative_id=p.initiative_id WHERE {$where}";
    $total_sql = 'SELECT COUNT(*)' . $base; $total = (int) $wpdb->get_var($params ? $wpdb->prepare($total_sql, $params) : $total_sql);
    $query = 'SELECT p.publication_id' . $base . ' ORDER BY p.published_at DESC,p.publication_id LIMIT %d OFFSET %d';
    $all_params = array_merge($params, array($size, ($page - 1) * $size));
    $ids = $wpdb->get_col($wpdb->prepare($query, $all_params));
    $items = array();
    foreach ($ids as $id) { $profile = gic_integration_public_profile($id); if (!is_wp_error($profile)) { $items[] = $profile; } }
    return rest_ensure_response(gic_integration_envelope($items, 'public_initiatives', array('pagination' => array('page' => $page, 'page_size' => $size, 'total' => $total, 'page_count' => (int) ceil($total / $size)))));
}
function gic_integration_public_publication_rest(WP_REST_Request $request) {
    $profile = gic_integration_public_profile(sanitize_text_field($request['id']));
    return is_wp_error($profile) ? $profile : rest_ensure_response(gic_integration_envelope($profile, 'public_publication'));
}
function gic_integration_api_key_auth(WP_REST_Request $request) {
    global $wpdb;
    $raw = trim((string) $request->get_header('x-gic-api-key'));
    if ($raw === '') {
        $auth = trim((string) $request->get_header('authorization'));
        if (stripos($auth, 'Bearer ') === 0) { $raw = trim(substr($auth, 7)); }
    }
    if ($raw === '') { return new WP_Error('gic_api_key_required', 'An API key is required.', array('status' => 401)); }
    $row = $wpdb->get_row($wpdb->prepare(
        'SELECT k.*,c.workspace_id,c.lifecycle_status FROM ' . gic_repository_table('api_keys') . ' k INNER JOIN ' . gic_repository_table('api_clients') . ' c ON c.client_id=k.client_id WHERE k.key_hash=%s',
        hash('sha256', $raw)
    ), ARRAY_A);
    if (!$row || !empty($row['revoked_at']) || $row['lifecycle_status'] !== 'active') { return new WP_Error('gic_api_key_invalid', 'The API key is invalid or inactive.', array('status' => 401)); }
    $scopes = json_decode($row['scopes_json'], true) ?: array();
    if (!in_array('workspace:read', $scopes, true)) { return new WP_Error('gic_api_scope', 'The API key lacks workspace:read.', array('status' => 403)); }
    $requested_workspace = sanitize_text_field($request->get_param('workspace_id') ?: '');
    if (!empty($row['workspace_id']) && $requested_workspace !== $row['workspace_id']) { return new WP_Error('gic_api_workspace', 'The API key is not authorized for this workspace.', array('status' => 403)); }
    $wpdb->update(gic_repository_table('api_keys'), array('last_used_at' => current_time('mysql', true)), array('api_key_id' => $row['api_key_id']));
    return true;
}
function gic_integration_workspace_resource_rest(WP_REST_Request $request) {
    global $wpdb;
    $workspace = sanitize_text_field($request->get_param('workspace_id'));
    $resource = sanitize_key($request['resource']);
    $map = array(
        'initiatives' => array('contracts', 'initiative_id'),
        'indicators' => array('indicator_definitions', 'indicator_definition_id'),
        'observations' => array('measurement_observations', 'observation_id'),
        'sources' => array('sources', 'source_id'),
        'reports' => array('report_documents', 'report_id'),
        'exports' => array('export_bundles', 'export_bundle_id'),
        'reviews' => array('review_assignments', 'assignment_id'),
    );
    if ($resource === 'workspace') {
        $row = $wpdb->get_row($wpdb->prepare('SELECT * FROM ' . gic_repository_table('entities') . " WHERE entity_type='workspace' AND entity_id=%s", $workspace), ARRAY_A);
        return rest_ensure_response(gic_integration_envelope($row, 'workspace'));
    }
    if (!isset($map[$resource])) { return new WP_Error('gic_api_resource', 'Unsupported workspace resource.', array('status' => 404)); }
    list($table_key, $id_field) = $map[$resource];
    $table = gic_repository_table($table_key);
    $page = max(1, (int) ($request->get_param('page') ?: 1)); $size = min(100, max(1, (int) ($request->get_param('page_size') ?: 50)));
    $total = (int) $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$table} WHERE workspace_id=%s", $workspace));
    $rows = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$table} WHERE workspace_id=%s ORDER BY {$id_field} LIMIT %d OFFSET %d", $workspace, $size, ($page - 1) * $size), ARRAY_A);
    return rest_ensure_response(gic_integration_envelope($rows, $resource, array('pagination' => array('page' => $page, 'page_size' => $size, 'total' => $total, 'page_count' => (int) ceil($total / $size)))));
}
function gic_integration_api_client_rest(WP_REST_Request $request) {
    global $wpdb;
    $p = $request->get_json_params(); $name = sanitize_text_field($p['name'] ?? '');
    if ($name === '') { return new WP_Error('gic_api_client_name', 'name is required.', array('status' => 400)); }
    $workspace = sanitize_text_field($p['workspace_id'] ?? ''); $now = current_time('mysql', true);
    $client_id = gic_integration_id('api-client', array($workspace, $name, microtime(true)));
    $scopes = array_values(array_intersect((array) ($p['scopes'] ?? array('workspace:read')), array('public:read','workspace:read','reports:read','exports:read','embeds:write','handoffs:write','audit:read')));
    $raw = 'gic_live_' . wp_generate_password(42, false, false); $key_hash = hash('sha256', $raw); $key_id = gic_integration_id('api-key', array($client_id, $key_hash));
    $wpdb->insert(gic_repository_table('api_clients'), array('client_id'=>$client_id,'workspace_id'=>$workspace,'name'=>$name,'client_type'=>sanitize_key($p['client_type']??'service'),'lifecycle_status'=>'active','rate_limit_per_minute'=>min(10000,max(1,(int)($p['rate_limit_per_minute']??60))),'scopes_json'=>wp_json_encode($scopes),'revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>'{}'));
    $wpdb->insert(gic_repository_table('api_keys'), array('api_key_id'=>$key_id,'client_id'=>$client_id,'key_prefix'=>substr($raw,0,16),'key_hash'=>$key_hash,'scopes_json'=>wp_json_encode($scopes),'expires_at'=>null,'revoked_at'=>null,'last_used_at'=>null,'created_at'=>$now,'metadata_json'=>'{}'));
    return rest_ensure_response(array('client_id'=>$client_id,'api_key_id'=>$key_id,'api_key'=>$raw,'scopes'=>$scopes,'notice'=>'Copy this key now. It will not be shown again.'));
}
function gic_integration_embed_rest(WP_REST_Request $request) {
    global $wpdb; $p = $request->get_json_params(); $publication_id = sanitize_text_field($p['publication_id'] ?? '');
    $profile = gic_integration_public_profile($publication_id); if (is_wp_error($profile)) { return $profile; }
    $snapshot_id = sanitize_text_field($p['publication_snapshot_id'] ?? $profile['snapshot']['snapshot_id']);
    if ($snapshot_id !== $profile['snapshot']['snapshot_id']) { return new WP_Error('gic_embed_snapshot', 'The selected snapshot is not the latest approved snapshot.', array('status'=>409)); }
    $type = sanitize_key($p['embed_type'] ?? 'initiative_card'); $allowed = array('initiative_card','indicator_trend','methodology_panel','portfolio_summary','report_view');
    if (!in_array($type, $allowed, true)) { return new WP_Error('gic_embed_type', 'Unsupported embed type.', array('status'=>400)); }
    $workspace = sanitize_text_field($p['workspace_id'] ?? ''); $slug = sanitize_title($p['public_slug'] ?? ($profile['initiative']['name'].'-'.$type)); $now=current_time('mysql',true);
    $content = array('publication_id'=>$publication_id,'snapshot_id'=>$snapshot_id,'snapshot_hash'=>$profile['snapshot']['snapshot_hash'],'embed_type'=>$type,'configuration'=>$p['configuration']??array(),'accessibility'=>$p['accessibility']??array('heading_level'=>2,'text_alternatives'=>true));
    $id=gic_integration_id('embed',array($workspace,$publication_id,$type,$slug));
    $wpdb->replace(gic_repository_table('embed_definitions'),array('embed_id'=>$id,'workspace_id'=>$workspace,'initiative_id'=>$profile['initiative']['id'],'publication_id'=>$publication_id,'publication_snapshot_id'=>$snapshot_id,'embed_type'=>$type,'title'=>sanitize_text_field($p['title']??$profile['publication']['title']),'public_slug'=>$slug,'configuration_json'=>wp_json_encode($content['configuration']),'accessibility_json'=>wp_json_encode($content['accessibility']),'content_hash'=>hash('sha256',wp_json_encode($content)),'lifecycle_status'=>'active','revision'=>1,'created_at'=>$now,'updated_at'=>$now,'metadata_json'=>'{}'));
    return rest_ensure_response(array('embed_id'=>$id,'public_slug'=>$slug,'content_hash'=>hash('sha256',wp_json_encode($content))));
}
function gic_integration_render_embed_data($slug) {
    global $wpdb; $embed=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.gic_repository_table('embed_definitions').' WHERE (public_slug=%s OR embed_id=%s) AND lifecycle_status=%s',$slug,$slug,'active'),ARRAY_A);
    if(!$embed)return new WP_Error('gic_embed_missing','Embed not found.',array('status'=>404));
    $profile=gic_integration_public_profile($embed['publication_id']);if(is_wp_error($profile))return $profile;
    $i=$profile['initiative'];$title=esc_html($embed['title']);$name=esc_html($i['name']);$type=$embed['embed_type'];$body='';
    if($type==='report_view'&&!empty($profile['report']['rendered_html'])){$body=wp_kses_post($profile['report']['rendered_html']);}
    elseif($type==='methodology_panel'){$m=$profile['report']['methodology']??array();$body='<dl><dt>Contract</dt><dd>'.esc_html($m['canonical_contract_version']??'').'</dd><dt>Sources</dt><dd>'.(int)($m['source_count']??0).'</dd><dt>Methods</dt><dd>'.(int)($m['method_count']??0).'</dd></dl>';}
    elseif($type==='indicator_trend'){$o=$i['latest_observation'];$body='<p class="gic-public-embed__metric">'.esc_html((string)$o['value']).' '.esc_html($o['unit']).'</p><p>'.esc_html($o['period']).'</p>';}
    else{$o=$i['latest_observation'];$body='<p>'.esc_html($i['goal']).'</p><dl><dt>Indicator</dt><dd>'.esc_html($i['indicator']['name']).'</dd><dt>Latest observation</dt><dd>'.esc_html((string)$o['value']).' '.esc_html($o['unit']).' · '.esc_html($o['period']).'</dd></dl>';}
    $html='<section class="gic-public-embed gic-public-embed--'.esc_attr($type).'" aria-labelledby="'.esc_attr($embed['embed_id']).'-title"><p class="gic-public-embed__eyebrow">Global Impact Catalyst · approved publication</p><h2 id="'.esc_attr($embed['embed_id']).'-title">'.$title.'</h2><h3>'.$name.'</h3>'.$body.'<p class="gic-public-embed__boundary">'.esc_html(gic_integration_boundary()).'</p></section>';
    return array('embed_id'=>$embed['embed_id'],'public_slug'=>$embed['public_slug'],'embed_type'=>$type,'snapshot_hash'=>$profile['snapshot']['snapshot_hash'],'html'=>$html);
}
function gic_integration_public_embed_rest(WP_REST_Request $request){$result=gic_integration_render_embed_data(sanitize_text_field($request['slug']));return is_wp_error($result)?$result:rest_ensure_response(gic_integration_envelope($result,'public_embed'));}
function gic_integration_handoff_rest(WP_REST_Request $request){
    global $wpdb;$p=$request->get_json_params();$destination=sanitize_key($p['destination']??'');$allowed=array('catalyst_data','catalyst_analytics_r','site_intelligence','workbench','research_lab','knowledge_library','research_librarian','decision_studio','platform_core','advisory');
    if(!in_array($destination,$allowed,true))return new WP_Error('gic_handoff_destination','Unsupported handoff destination.',array('status'=>400));
    $workspace=sanitize_text_field($p['workspace_id']??'');$initiative=sanitize_text_field($p['initiative_id']??'');$idempotency=sanitize_text_field($p['idempotency_key']??'');
    if($idempotency!==''){$existing=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.gic_repository_table('platform_handoffs').' WHERE workspace_id=%s AND destination=%s AND idempotency_key=%s',$workspace,$destination,$idempotency),ARRAY_A);if($existing){$existing['payload']=json_decode($existing['payload_json'],true);unset($existing['payload_json']);$existing['idempotent_replay']=true;return rest_ensure_response($existing);}}
    $contracts=$wpdb->get_results($wpdb->prepare('SELECT record_id,initiative_id,content_hash,contract_json FROM '.gic_repository_table('contracts').' WHERE workspace_id=%s'.($initiative!==''?' AND initiative_id=%s':''),...array_filter(array($workspace,$initiative),static function($v){return $v!=='';})),ARRAY_A);
    $reports=$wpdb->get_results($wpdb->prepare('SELECT report_id,initiative_id,title,content_hash,document_json FROM '.gic_repository_table('report_documents').' WHERE workspace_id=%s',$workspace),ARRAY_A);
    $payload=array('@context'=>gic_integration_jsonld_context(),'handoff_type'=>'global_impact_platform_handoff','handoff_version'=>'1.9.0','destination'=>$destination,'created_at'=>gmdate('c'),'source_snapshot_hash'=>hash('sha256',wp_json_encode(array($contracts,$reports))),'data'=>array('workspace_id'=>$workspace,'initiative_id'=>$initiative,'contracts'=>$contracts,'reports'=>$reports,'receiving_contract'=>$destination.'/1.9.0'),'boundary'=>'Handoff integrity preserves source identity and governance metadata; receiving systems must retain limitations and may not infer assurance or causal proof.');
    $payload_hash=hash('sha256',wp_json_encode($payload));$id=gic_integration_id('handoff',array($workspace,$destination,$initiative,$payload_hash));$now=current_time('mysql',true);
    $wpdb->insert(gic_repository_table('platform_handoffs'),array('handoff_id'=>$id,'workspace_id'=>$workspace,'initiative_id'=>$initiative,'destination'=>$destination,'handoff_version'=>'1.9.0','status'=>'ready','source_snapshot_hash'=>$payload['source_snapshot_hash'],'payload_hash'=>$payload_hash,'payload_json'=>wp_json_encode($payload),'idempotency_key'=>$idempotency,'created_at'=>$now,'delivered_at'=>null,'delivery_receipt_json'=>'{}','metadata_json'=>'{}'));
    return rest_ensure_response(array('handoff_id'=>$id,'destination'=>$destination,'payload_hash'=>$payload_hash,'payload'=>$payload));
}
function gic_integration_repository_rest(WP_REST_Request $request){
    global $wpdb;$workspace=sanitize_text_field($request->get_param('workspace_id')?:'');
    $clients=$wpdb->get_results($wpdb->prepare('SELECT client_id,workspace_id,name,client_type,lifecycle_status,rate_limit_per_minute,scopes_json,revision,created_at,updated_at FROM '.gic_repository_table('api_clients').' WHERE workspace_id=%s',$workspace),ARRAY_A);
    foreach($clients as &$client){$client['scopes']=json_decode($client['scopes_json'],true);unset($client['scopes_json']);}unset($client);
    $embeds=$wpdb->get_results($wpdb->prepare('SELECT * FROM '.gic_repository_table('embed_definitions').' WHERE workspace_id=%s ORDER BY title',$workspace),ARRAY_A);
    $handoffs=$wpdb->get_results($wpdb->prepare('SELECT * FROM '.gic_repository_table('platform_handoffs').' WHERE workspace_id=%s ORDER BY created_at',$workspace),ARRAY_A);
    foreach($handoffs as &$handoff){$handoff['payload']=json_decode($handoff['payload_json'],true);unset($handoff['payload_json']);$handoff['integrity']=array('valid'=>hash_equals($handoff['payload_hash'],hash('sha256',wp_json_encode($handoff['payload']))));}unset($handoff);
    $repository=array('repository_type'=>'global_impact_integration_repository','repository_version'=>'1.9.0','api_version'=>'v1','workspace_id'=>$workspace,'generated_at'=>gmdate('c'),'jsonld_context'=>gic_integration_jsonld_context(),'api_clients'=>$clients,'embeds'=>$embeds,'platform_handoffs'=>$handoffs,'integration_events'=>array(),'api_access_log'=>array(),'integrity'=>array('valid'=>!in_array(false,array_map(static function($h){return $h['integrity']['valid'];},$handoffs),true),'api_client_count'=>count($clients),'embed_count'=>count($embeds),'handoff_count'=>count($handoffs),'event_count'=>0,'access_log_count'=>0,'broken_embed_ids'=>array(),'broken_handoff_ids'=>array_values(array_map(static function($h){return $h['handoff_id'];},array_filter($handoffs,static function($h){return !$h['integrity']['valid'];}))),'broken_event_ids'=>array()),'privacy'=>array('api_key_material_exported'=>false,'public_data_requires_published_snapshot'=>true,'raw_evidence_excerpts_public'=>false),'boundary'=>gic_integration_boundary());
    return rest_ensure_response($repository);
}
function gic_integration_register_routes(){
    register_rest_route('global-impact-catalyst/v1','/public/initiatives',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_integration_public_catalog_rest','permission_callback'=>'__return_true'));
    register_rest_route('global-impact-catalyst/v1','/public/publications/(?P<id>[A-Za-z0-9._-]+)',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_integration_public_publication_rest','permission_callback'=>'__return_true'));
    register_rest_route('global-impact-catalyst/v1','/public/embeds/(?P<slug>[A-Za-z0-9._-]+)',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_integration_public_embed_rest','permission_callback'=>'__return_true'));
    register_rest_route('global-impact-catalyst/v1','/workspace/(?P<resource>[A-Za-z0-9._-]+)',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_integration_workspace_resource_rest','permission_callback'=>'gic_integration_api_key_auth'));
    register_rest_route('global-impact-catalyst/v1','/api-clients',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_integration_api_client_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/embeds',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_integration_embed_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/platform-handoffs',array('methods'=>WP_REST_Server::CREATABLE,'callback'=>'gic_integration_handoff_rest','permission_callback'=>'gic_repository_can_edit'));
    register_rest_route('global-impact-catalyst/v1','/integration-repository',array('methods'=>WP_REST_Server::READABLE,'callback'=>'gic_integration_repository_rest','permission_callback'=>'gic_repository_can_edit'));
}
add_action('rest_api_init','gic_integration_register_routes');
function gic_integration_hub_shortcode($atts=array()){
    if(!is_user_logged_in()||!current_user_can('edit_posts'))return '<p class="gic-integration__login">Sign in with editing access to use the Integration Hub.</p>';
    wp_enqueue_style('global-impact-catalyst-integration');wp_enqueue_script('global-impact-catalyst-integration');ob_start();?>
<section class="gic-integration" data-gic-integration-hub data-rest="<?php echo esc_url(rest_url('global-impact-catalyst/v1/')); ?>" data-nonce="<?php echo esc_attr(wp_create_nonce('wp_rest')); ?>"><header class="gic-integration__header"><p class="gic-integration__eyebrow">Connected platform service · v1.9.0</p><h2>Public API, Embeds, and Platform Handoffs</h2><p>Manage scoped API clients, approved public embeds, and checksum-bound handoffs to Sustainable Catalyst products.</p><p class="gic-integration__boundary"><?php echo esc_html(gic_integration_boundary()); ?></p></header><div class="gic-integration__grid"><div class="gic-integration__panel"><h3>Integration context</h3><label>Workspace ID<input name="workspace_id"></label><label>Initiative ID<input name="initiative_id"></label><label>Publication ID<input name="publication_id"></label><label>Publication snapshot ID<input name="publication_snapshot_id"></label><label>Destination<select name="destination"><option>catalyst_data</option><option>catalyst_analytics_r</option><option>site_intelligence</option><option>workbench</option><option>research_lab</option><option>knowledge_library</option><option>research_librarian</option><option>decision_studio</option><option>platform_core</option><option>advisory</option></select></label><label>Embed type<select name="embed_type"><option>initiative_card</option><option>indicator_trend</option><option>methodology_panel</option><option>portfolio_summary</option><option>report_view</option></select></label><div class="gic-integration__actions"><button type="button" data-gic-integration-load>Load repository</button><button type="button" data-gic-integration-client>Create API client</button><button type="button" data-gic-integration-embed>Create embed</button><button type="button" data-gic-integration-handoff>Create handoff</button></div></div><div class="gic-integration__panel"><h3>Integration output</h3><pre data-gic-integration-results aria-live="polite">Enter a workspace ID to begin.</pre></div></div></section><?php return ob_get_clean();}
add_shortcode('global_impact_catalyst_integration_hub','gic_integration_hub_shortcode');
function gic_public_profile_shortcode($atts=array()){$a=shortcode_atts(array('publication_id'=>''),$atts);$profile=gic_integration_public_profile(sanitize_text_field($a['publication_id']));if(is_wp_error($profile))return '<p class="gic-public-error">'.esc_html($profile->get_error_message()).'</p>';$i=$profile['initiative'];return '<section class="gic-public-profile"><p class="gic-public-profile__eyebrow">Approved impact profile</p><h2>'.esc_html($i['name']).'</h2><p>'.esc_html($i['goal']).'</p><dl><dt>Indicator</dt><dd>'.esc_html($i['indicator']['name']).'</dd><dt>Latest observation</dt><dd>'.esc_html((string)$i['latest_observation']['value']).' '.esc_html($i['latest_observation']['unit']).' · '.esc_html($i['latest_observation']['period']).'</dd></dl><p class="gic-public-profile__boundary">'.esc_html(gic_integration_boundary()).'</p></section>';}
function gic_public_indicator_shortcode($atts=array()){$a=shortcode_atts(array('publication_id'=>''),$atts);$profile=gic_integration_public_profile(sanitize_text_field($a['publication_id']));if(is_wp_error($profile))return '<p class="gic-public-error">'.esc_html($profile->get_error_message()).'</p>';$i=$profile['initiative'];return '<section class="gic-public-indicator"><h2>'.esc_html($i['indicator']['name']).'</h2><p>'.esc_html($i['indicator']['definition']).'</p><p class="gic-public-indicator__value">'.esc_html((string)$i['latest_observation']['value']).' '.esc_html($i['latest_observation']['unit']).'</p><p>'.esc_html($i['latest_observation']['period']).'</p></section>';}
function gic_public_report_shortcode($atts=array()){$a=shortcode_atts(array('publication_id'=>''),$atts);$profile=gic_integration_public_profile(sanitize_text_field($a['publication_id']));if(is_wp_error($profile))return '<p class="gic-public-error">'.esc_html($profile->get_error_message()).'</p>';return !empty($profile['report']['rendered_html'])?wp_kses_post($profile['report']['rendered_html']):'<p>No approved report is attached to this publication.</p>';}
function gic_compact_embed_shortcode($atts=array()){$a=shortcode_atts(array('slug'=>''),$atts);$result=gic_integration_render_embed_data(sanitize_text_field($a['slug']));return is_wp_error($result)?'<p class="gic-public-error">'.esc_html($result->get_error_message()).'</p>':$result['html'];}
add_shortcode('global_impact_catalyst_public_profile','gic_public_profile_shortcode');
add_shortcode('global_impact_catalyst_indicator_view','gic_public_indicator_shortcode');
add_shortcode('global_impact_catalyst_report_view','gic_public_report_shortcode');
add_shortcode('global_impact_catalyst_compact_embed','gic_compact_embed_shortcode');
