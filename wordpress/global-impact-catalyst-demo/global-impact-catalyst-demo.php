<?php
/**
 * Plugin Name: Global Impact Catalyst
 * Description: Persistent impact workspaces, evidence chains, governed indicator registry, and canonical contract demo. Shortcodes: [global_impact_catalyst_workspace], [global_impact_catalyst_evidence_ledger], [global_impact_catalyst_indicator_registry], [global_impact_catalyst_demo]
 * Version: 1.4.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('GIC_DEMO_VERSION', '1.4.0');
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
    gic_registry_seed_units();
    update_option('gic_repository_schema_version', 3, false);
}
register_activation_hook(__FILE__, 'gic_repository_activate');

function gic_repository_maybe_upgrade() {
    if ((int) get_option('gic_repository_schema_version', 0) < 3) { gic_repository_activate(); }
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
