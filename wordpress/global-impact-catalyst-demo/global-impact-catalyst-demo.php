<?php
/**
 * Plugin Name: Global Impact Catalyst
 * Description: Persistent impact workspaces, evidence chains, and canonical contract demo. Shortcodes: [global_impact_catalyst_workspace], [global_impact_catalyst_evidence_ledger], [global_impact_catalyst_demo]
 * Version: 1.3.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('GIC_DEMO_VERSION', '1.3.0');
define('GIC_DEMO_URL', plugin_dir_url(__FILE__));

function gic_demo_register_assets() {
    wp_register_style('global-impact-catalyst-demo', GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.css', array(), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-demo', GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.js', array(), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-workspace', GIC_DEMO_URL . 'assets/global-impact-catalyst-workspace.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-workspace', GIC_DEMO_URL . 'assets/global-impact-catalyst-workspace.js', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION, true);
    wp_register_style('global-impact-catalyst-evidence', GIC_DEMO_URL . 'assets/global-impact-catalyst-evidence.css', array('global-impact-catalyst-demo'), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-evidence', GIC_DEMO_URL . 'assets/global-impact-catalyst-evidence.js', array(), GIC_DEMO_VERSION, true);
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
    update_option('gic_repository_schema_version', 2, false);
}
register_activation_hook(__FILE__, 'gic_repository_activate');

function gic_repository_maybe_upgrade() {
    if ((int) get_option('gic_repository_schema_version', 0) < 2) { gic_repository_activate(); }
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
