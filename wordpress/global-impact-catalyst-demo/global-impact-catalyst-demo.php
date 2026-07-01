<?php
/**
 * Plugin Name: Global Impact Catalyst Demo
 * Description: Browser-based Global Impact Catalyst demo for traceable impact measurement records. Shortcode: [global_impact_catalyst_demo]
 * Version: 1.0.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('GIC_DEMO_VERSION', '1.0.0');
define('GIC_DEMO_URL', plugin_dir_url(__FILE__));
define('GIC_DEMO_PATH', plugin_dir_path(__FILE__));

function gic_demo_register_assets() {
    wp_register_style(
        'global-impact-catalyst-demo',
        GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.css',
        array(),
        GIC_DEMO_VERSION
    );

    wp_register_script(
        'global-impact-catalyst-demo',
        GIC_DEMO_URL . 'assets/global-impact-catalyst-demo.js',
        array(),
        GIC_DEMO_VERSION,
        true
    );
}
add_action('wp_enqueue_scripts', 'gic_demo_register_assets');

function gic_demo_shortcode($atts = array()) {
    wp_enqueue_style('global-impact-catalyst-demo');
    wp_enqueue_script('global-impact-catalyst-demo');

    ob_start();
    ?>
    <section class="gic-demo" data-gic-demo>
      <div class="gic-demo__header">
        <p class="gic-demo__eyebrow">Interactive demo</p>
        <h2>Build a Traceable Impact Record</h2>
        <p>
          Enter a goal, indicator, source, and measurement values. The demo estimates progress to target,
          flags review status, and exports a structured record for inspection.
        </p>
      </div>

      <div class="gic-demo__grid">
        <form class="gic-demo__form" data-gic-form>
          <div class="gic-demo__field gic-demo__field--wide">
            <label for="gic-initiative">Initiative or program</label>
            <input id="gic-initiative" name="initiative" type="text" value="Community Energy Retrofit Pilot">
          </div>

          <div class="gic-demo__field gic-demo__field--wide">
            <label for="gic-goal">Impact goal</label>
            <textarea id="gic-goal" name="goal" rows="3">Reduce household energy burden while improving residential efficiency.</textarea>
          </div>

          <div class="gic-demo__field">
            <label for="gic-theme">SDG-style theme</label>
            <select id="gic-theme" name="sdgTheme">
              <option>Affordable and clean energy</option>
              <option>Climate action</option>
              <option>Sustainable cities and communities</option>
              <option>Responsible consumption and production</option>
              <option>Good health and well-being</option>
              <option>Quality education</option>
              <option>Reduced inequalities</option>
            </select>
          </div>

          <div class="gic-demo__field">
            <label for="gic-indicator">Indicator</label>
            <input id="gic-indicator" name="indicator" type="text" value="Average monthly bill reduction">
          </div>

          <div class="gic-demo__field">
            <label for="gic-unit">Unit</label>
            <input id="gic-unit" name="unit" type="text" value="USD">
          </div>

          <div class="gic-demo__field">
            <label for="gic-direction">Direction</label>
            <select id="gic-direction" name="higherIsBetter">
              <option value="true" selected>Higher is better</option>
              <option value="false">Lower is better</option>
            </select>
          </div>

          <div class="gic-demo__field">
            <label for="gic-baseline-period">Baseline period</label>
            <input id="gic-baseline-period" name="baselinePeriod" type="text" value="2025 baseline">
          </div>

          <div class="gic-demo__field">
            <label for="gic-current-period">Current period</label>
            <input id="gic-current-period" name="currentPeriod" type="text" value="2026 Q2">
          </div>

          <div class="gic-demo__field">
            <label for="gic-baseline">Baseline value</label>
            <input id="gic-baseline" name="baseline" type="number" step="0.01" value="0">
          </div>

          <div class="gic-demo__field">
            <label for="gic-current">Current value</label>
            <input id="gic-current" name="current" type="number" step="0.01" value="18">
          </div>

          <div class="gic-demo__field">
            <label for="gic-target">Target value</label>
            <input id="gic-target" name="target" type="number" step="0.01" value="30">
          </div>

          <div class="gic-demo__field">
            <label for="gic-beneficiaries">Beneficiaries</label>
            <input id="gic-beneficiaries" name="beneficiaries" type="number" step="1" value="420">
          </div>

          <div class="gic-demo__field">
            <label for="gic-budget">Budget USD</label>
            <input id="gic-budget" name="budget" type="number" step="1" value="125000">
          </div>

          <div class="gic-demo__field">
            <label for="gic-confidence">Confidence</label>
            <select id="gic-confidence" name="confidence">
              <option value="low">Low</option>
              <option value="medium" selected>Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div class="gic-demo__field">
            <label for="gic-review">Review status</label>
            <select id="gic-review" name="reviewStatus">
              <option value="draft">Draft</option>
              <option value="needs_review" selected>Needs review</option>
              <option value="reviewed">Reviewed</option>
              <option value="published">Published</option>
            </select>
          </div>

          <div class="gic-demo__field gic-demo__field--wide">
            <label for="gic-source">Source</label>
            <input id="gic-source" name="source" type="text" value="Pilot utility-billing sample and participant survey summary">
          </div>

          <div class="gic-demo__field gic-demo__field--wide">
            <label for="gic-method">Method notes</label>
            <textarea id="gic-method" name="method" rows="4">Current value is the observed average monthly bill reduction across participating households compared with baseline average bills. Results should be reviewed for seasonality and household-size differences.</textarea>
          </div>

          <div class="gic-demo__actions">
            <button type="submit">Generate Record</button>
            <button type="button" data-gic-reset>Reset Example</button>
            <button type="button" data-gic-download>Download JSON</button>
          </div>
        </form>

        <aside class="gic-demo__output" aria-live="polite">
          <div class="gic-demo__scorecard">
            <div>
              <span>Progress to target</span>
              <strong data-gic-progress>—</strong>
            </div>
            <div>
              <span>Data quality</span>
              <strong data-gic-quality>—</strong>
            </div>
            <div>
              <span>Status</span>
              <strong data-gic-status>—</strong>
            </div>
          </div>

          <div class="gic-demo__bar" aria-hidden="true"><span data-gic-bar></span></div>

          <div class="gic-demo__result" data-gic-result>
            <h3>Impact Record</h3>
            <p>Generate a record to see the interpretation notes and traceability path.</p>
          </div>

          <details class="gic-demo__json">
            <summary>View JSON export</summary>
            <pre data-gic-json>{}</pre>
          </details>
        </aside>
      </div>

      <p class="gic-demo__boundary">
        Educational demo only. This is not SDG certification, ESG assurance, legal advice, or automatic truth verification.
      </p>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('global_impact_catalyst_demo', 'gic_demo_shortcode');
