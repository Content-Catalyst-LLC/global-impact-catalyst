<?php
/**
 * Plugin Name: Global Impact Catalyst Demo
 * Description: Browser-based canonical impact contract and validation demo. Shortcode: [global_impact_catalyst_demo]
 * Version: 1.1.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('GIC_DEMO_VERSION', '1.1.0');
define('GIC_DEMO_URL', plugin_dir_url(__FILE__));

function gic_demo_register_assets() {
    wp_register_style('global-impact-catalyst-demo', GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.css', array(), GIC_DEMO_VERSION);
    wp_register_script('global-impact-catalyst-demo', GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.js', array(), GIC_DEMO_VERSION, true);
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
        <p class="gic-demo__eyebrow">Canonical contract demo · v1.1.0</p>
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
